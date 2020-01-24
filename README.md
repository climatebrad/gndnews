# News for a Green New Deal
## Goal: Find and Organize Climate-Related News
As a long-time climate journalist and activist, I have worked for years to transform the firehose of daily news into coherent stories that provide space for action.
The goal of this project is to organize and classify news articles and potentially other written material by climate-related subtopics based on textual content.

## Why is this important?
Man-made global warming is the existential challenge of our time. To build a carbon-free, resilient, and just society, citizens need to learn how the fossil-fuel economy interacts with every aspect of our lives, and how the damages of the pollution are reshaping our world. 
Most news and media is not organized to tell that story coherently. For example, extreme weather, political corruption, and energy finance are treated as disjoint, not interconnected topics.

This project is a step towards a high-quality climate news aggregator, applicable to other areas of interest as well.

[News for a Green New Deal Presentation](News%20for%20a%20Green%20New%20Deal%20Presentation.pdf)

## Scraping

* [earther_scraper/](earther_scraper/) - Earther.com webscraper
* [gizmodo_scraper/](gizmodo_scraper/) - Gizmodo.com webscraper

## Modeling
[pipeline.py](pipeline.py) - Modeling steps

* [topic_modeler/modeler.py](topic_modeler/modeler.py) - base Modeler object
* [topic_modeler/clustering.py](topic_modeler/clustering.py) - Topic clustering functions
* [topic_modeler/modeling.py](topic_modeler/modeling.py) - Article text classifier functions
* [topic_modeler/newsifier.py](topic_modeler/newsifier.py) - Presentation and deployment functions

[topic_modeler/gizmodo_modeler.py](topic_modeler/gizmodo_modeler.py) - Subclass of Modeler to do Gizmodo modeling

## Deployment
A Flask app using the trained model analyzes text and returns probability ratings for associated topics.

Deployed at: [green-new-deal-news.herokuapp.com](https://green-new-deal-news.herokuapp.com)
