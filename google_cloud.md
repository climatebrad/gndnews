How to get python 3.7 working on Google Cloud Notebooks. 
Create instance (the boot disk needs to be Linux e.g. Debian or Ubuntu).
Easiest is to use AI Platform to create a notebook instance (sets up JupyterLab.)
```
https://console.cloud.google.com/ai-platform/notebooks/instances
https://cloud.google.com/compute/docs/quickstart-linux
```

SSH to the instance:

```
# install necessary command-line tools
sudo apt-get install -y build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev zlib1g-dev openssl libffi-dev python3-dev python3-setuptools wget git

#install pyenv to install python on persistent home directory

curl https://pyenv.run | bash

# add to path
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# install python 3.7.4 and make default
pyenv install 3.7.4
pyenv global 3.7.4

python -m pip install ipykernel

python -m ipykernel install --user --name python-37 --display-name "Python 3.7"
```
If Jupyter Lab is already installed, restart kernel

otherwise
```
pip install jupyterlab
```

need to install packages e.g.
```
pip install pandas scikit-learn joblib imbalanced-learn pymongo matplotlib

