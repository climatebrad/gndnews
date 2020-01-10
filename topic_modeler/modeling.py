import re
import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA
import nltk
from nltk.corpus import stopwords
import string
from nltk import word_tokenize, FreqDist
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_samples, silhouette_score

class Modeler():
    """Modeling object"""
    def __init__(self):
        self._articles = None
        self._keywords = None
        self._vectorized_keywords = None
        self._k_means = None
        self._gizmodo_stop_words = None
        
    gizmodo_properties = {'earther' : 'environment',
                          'gizmodo' : 'general interest',
                          'lifehacker' : 'self-improvement',
                          'the root' : 'African-American',
                          'jalopnik' : 'cars',
                          'deadspin' : 'sports',
                          'i09' : 'nerd culture',
                          'the takeout' : 'food',
                          'jezebel' : 'feminism',
                          'paleofuture' : 'general interest',
                          'the slot' : 'feminist politics',
                          'kotaku' : 'video games',
                          'the muse$' : 'feminist culture',
                          'the concourse' : 'general interest',
                          'the onion' : 'satire'}
    
    gizmodo_regex = re.compile('(' + '|'.join(gizmodo_properties) + ')', re.IGNORECASE)
    
    def convert_gizmodo(self, kwd):
        """convert a keyword that includes a gizmodo property to its general category"""
        if self.gizmodo_regex.search(kwd):
                match = self.gizmodo_regex.search(kwd)[0].lower()
                if match == 'the muse':
                    match = 'the muse$'
                return self.gizmodo_properties[match]
        return kwd

    @property 
    def articles(self):
        """load articles into dataframe from mongodb"""
        if self._articles is None:
            myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
            mydb = myclient['items']
            mycollection = mydb['articles']
            articles = pd.DataFrame(list(mycollection.find({})))
            articles.created_at = pd.to_datetime(articles.created_at, infer_datetime_format=True)
            self._articles = articles
        return self._articles
    
    @property
    def keywords(self):
        """the keywords column from data into its own dataframe"""
        if self._keywords is None:
            self._keywords = pd.DataFrame(self.articles.keywords.copy())
        return self._keywords
    
    @property
    def gizmodo_stop_words(self):
        if self._gizmodo_stop_words is None:
            keyword_list = set(self.keywords.sum()[0])
            self._gizmodo_stop_words = list(filter(self.gizmodo_regex.search, keyword_list))
        return self._gizmodo_stop_words
    
    @staticmethod
    def preprocess_token(token):
        """lowercase, replace spaces with underscore"""
        return token.replace(' ','_').lower()

    def vectorize_keywords(self, vectorizer='count', gizmodo='ignore', **params):
        """Return dataframe of vectorized self.keywords. 
        vectorizer can be 'count' or 'tfidf'
        if gizmodo='ignore', stop_words include gizmodo properties.
        if gizmodo='convert', names of gizmodo properties are changed to subject-matter keywords
        additional named params passed to CountVectorizer() or TfIdfVectorizer()"""
        key_df = self.keywords.copy()                       
        stop_words = params.pop('stop_words', [])
        if gizmodo == 'true':
            stop_words.extend([self.preprocess_token(k) for k in self.gizmodo_stop_words])
        elif gizmodo == 'convert':
            key_df.keywords = key_df.keywords.apply(lambda lst : [self.convert_gizmodo(x) for x in lst])
        
        if vectorizer == 'tfidf':
            vect = TfidfVectorizer(stop_words=stop_words, **params)
        else:
            vect = CountVectorizer(stop_words=stop_words, **params)

        X = vect.fit_transform(key_df.pop('keywords').map(lambda lst : ' '.join([self.preprocess_token(k) for k in lst])))
        for i, col in enumerate(vect.get_feature_names()):
            key_df[col] = pd.Series(X[:, i].toarray().ravel())
        self._vectorized_keywords = key_df
        return key_df
        
    @property
    def vectorized_keywords(self):
        if self._vectorized_keywords is None:
            raise Exception("Keywords have not been vectorized. Run Modeler.vectorize_keywords().")
        return self._vectorized_keywords
    
    @property
    def k_means(self):
        if self._k_means is None:
            raise Exception("k_means not defined. Run Modeler.cluster_keywords()")
        return self._k_means
    
    def cluster_keywords(self, n_clusters : int, random_state=10):
        """Run K-Means clustering on vectorized keywords, update articles.cluster column with predictions
        default random_state is 10."""
        k_means = KMeans(n_clusters=n_clusters, random_state=random_state)
        k_means.fit(self.vectorized_keywords)
        self.articles['cluster'] = k_means.predict(self.vectorized_keywords)
        self._k_means = k_means
        return k_means


    def save_clusters_to_mongodb(self):
        
    def display_keyword_clusters(self, n_keywords=20, ignore_gizmodo=True):
        """Return dataframe of clusters with top n_keywords in descending order. 
        if ignore_gizmode=True, don't display keywords with gizmodo properties."""
        if 'cluster' not in self.articles:
            raise Exception("Clusters not defined. Run Modeler.cluster_keywords(n_clusters)")
        clusters = {}
        for i in range(self.articles.cluster.max() + 1):
            cluster_kwds = self.articles[self.articles.cluster == i].keywords.sum()
            if ignore_gizmodo:
                cluster_kwds = [kwd for kwd in cluster_kwds if kwd not in self.gizmodo_stop_words]
            clusters[i] = (pd.Series(cluster_kwds)
                           .value_counts()
                           .head(n_keywords)
                           .reset_index()[['index',0]]
                           .apply(lambda x : x.astype(str))
                           .apply(" ".join, axis=1))
        return pd.DataFrame(clusters)
    
    def display_reduced_keyword_clusters(self):
        """Show of plot of the keyword clusters in 2 dimensions"""
        reduced_data = PCA(n_components=2).fit_transform(self.vectorized_keywords)
        self.k_means.fit(reduced_data)

        # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
        y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        # Obtain labels for each point in mesh. Use last trained model.
        Z = self.k_means.predict(np.c_[xx.ravel(), yy.ravel()])

        # Put the result into a color plot
        Z = Z.reshape(xx.shape)
        plt.figure(1, (15, 15))
        plt.clf()
        plt.imshow(Z, interpolation='nearest',
                   extent=(xx.min(), xx.max(), yy.min(), yy.max()),
                   cmap=plt.cm.Paired,
                   aspect='auto', origin='lower')

        plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
        # Plot the centroids as a white X
        centroids = self.k_means.cluster_centers_
        plt.scatter(centroids[:, 0], centroids[:, 1],
                    marker='x', s=169, linewidths=3,
                    color='w', zorder=10)
        plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
                  'Centroids are marked with white cross')
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xticks(())
        plt.yticks(())
        plt.show()
        
    def silhouette_analysis(self, start=4, end=15, random_state=10):
        """Prints out average silhouette score and diagrams for kmeans clusters from start to end on vectorized keywords.
        Default random_state for KMeans instance is 10."""
        range_n_clusters = range(start, end+1)
        X = self.vectorized_keywords
        X_2d = PCA(n_components=2).fit_transform(X)
        silhouette_avg = {}
        for n_clusters in range_n_clusters:
            # Create a subplot with 1 row and 2 columns
            fig, (ax1, ax2) = plt.subplots(1, 2)
            fig.set_size_inches(18, 7)

            # The 1st subplot is the silhouette plot
            # The silhouette coefficient can range from -1, 1 but in this example all
            # lie within [-0.1, 1]
            ax1.set_xlim([-0.1, 1])
            # The (n_clusters+1)*10 is for inserting blank space between silhouette
            # plots of individual clusters, to demarcate them clearly.
            ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

            # Initialize the clusterer with n_clusters value 
            # note random_state not set
            clusterer = KMeans(n_clusters=n_clusters, random_state=random_state)
            cluster_labels = clusterer.fit_predict(X)

            # The silhouette_score gives the average value for all the samples.
            # This gives a perspective into the density and separation of the formed
            # clusters
            silhouette_avg[n_clusters] = silhouette_score(X, cluster_labels)
            print("For n_clusters =", n_clusters,
                  "The average silhouette_score is :", silhouette_avg[n_clusters])

            # Compute the silhouette scores for each sample
            sample_silhouette_values = silhouette_samples(X, cluster_labels)

            y_lower = 10
            for i in range(n_clusters):
                # Aggregate the silhouette scores for samples belonging to
                # cluster i, and sort them
                ith_cluster_silhouette_values = \
                    sample_silhouette_values[cluster_labels == i]

                ith_cluster_silhouette_values.sort()

                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i

                color = cm.nipy_spectral(float(i) / n_clusters)
                ax1.fill_betweenx(np.arange(y_lower, y_upper),
                                  0, ith_cluster_silhouette_values,
                                  facecolor=color, edgecolor=color, alpha=0.7)

                # Label the silhouette plots with their cluster numbers at the middle
                ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

                # Compute the new y_lower for next plot
                y_lower = y_upper + 10  # 10 for the 0 samples

            ax1.set_title("The silhouette plot for the various clusters.")
            ax1.set_xlabel("The silhouette coefficient values")
            ax1.set_ylabel("Cluster label")

            # The vertical line for average silhouette score of all the values
            ax1.axvline(x=silhouette_avg[n_clusters], color="red", linestyle="--")

            ax1.set_yticks([])  # Clear the yaxis labels / ticks
            ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

            # 2nd Plot showing the actual clusters formed
            colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
            ax2.scatter(X_2d[:, 0], X_2d[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                        c=colors, edgecolor='k')

            # Labeling the clusters
            centers = clusterer.cluster_centers_
            # Draw white circles at cluster centers
            ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
                        c="white", alpha=1, s=200, edgecolor='k')

            for i, c in enumerate(centers):
                ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
                            s=50, edgecolor='k')

            ax2.set_title("The visualization of the clustered data.")
            ax2.set_xlabel("Feature space for the 1st feature")
            ax2.set_ylabel("Feature space for the 2nd feature")

            plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                          "with n_clusters = %d" % n_clusters),
                         fontsize=14, fontweight='bold')

        plt.show()
        return silhouette_avg