python --version
PROJECT="harvest-reporting"

CODE_HOME=~/Builds/$PROJECT/code
PYENV_HOME=~/Builds/$PROJECT/python
export PYENV_HOME
export PYTHONPATH=""
echo "Creating new Python env"
/usr/local/bin/python3 -m venv  --clear $PYENV_HOME
source $PYENV_HOME/bin/activate

echo "Copy Project"
mkdir -p ~/Builds
mkdir -p $CODE_HOME
cp -a . $CODE_HOME
cd $CODE_HOME

pip install --upgrade pip
pip install nose
pip install coverage
pip install -r requirements.txt
