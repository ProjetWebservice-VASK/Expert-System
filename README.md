Expert-System
=============

[![Build Status](https://travis-ci.org/ProjetWebservice-VASK/Expert-System.svg)](https://travis-ci.org/ProjetWebservice-VASK/Expert-System)

Python based Expert System to answer pending questions on the Question Server

### Installing on your local environment

Prerequisites :
* Python
* pip
* virtualenv (pip install --user virtualenv)
* Command line interface

Go to your local workspace
```
cd /path/to/your/workspace/
```
Clone the project from Github
``` 
git clone https://github.com/ProjetWebservice-VASK/Expert-System.git
```
Create a virtual environment
```
cd Expert-System
virtualenv env
```
Enter the virtual environment
```
source env/bin/activate
```
That's it your ready to code !

### Adding dependencies

To make sure the dependencies are included in the next commit, you must save the current dependencies in the ***requirements.txt*** file to ensure that every development environment is up to date.

While in the virtual environment
```
pip freeze -l > /path/to/your/workspace/Expert-System/requirements.txt
```

### Licence

This project is covered by the MIT Licence, feel free to reuse it.


