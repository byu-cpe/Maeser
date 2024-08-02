# Setting Set Up To Use Maeser

There are two possible use models for you as a user. The first is if you simply want to develop your own app that uses Maeser. That is the focus of this document. If, instead, you want to clone and start making changes to the Maeser code base itself, you should instead consult [this documentation](development_setup.md).

## Step 1: Create a Virtual Environment

You will need to use a python virtual environment for your system. This is so that (1) you don't have to install packages system-wide (which you may not have privileges to do on the system you are working with) and (2) so that you have total control over the installed software versions. This includes the version of python you are using - at the current time python >= version 3.0 is required.

We will outline the use of Conda here since it provides the simplest way to get a virtual environment with a specific python version. However, you are free to use your favorite python virtual environment approach instead.

1. You can install Conda using:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
```

Note that for Mac OS X, replacing Linux with MacOSX in the first command above will do the trick. Also, depending on your system you may be able to (or need to) use `curl` instead of `wget` above.

2. Next, make a new virtual environment with a specific version of python with the following:

`conda create --name maeserEnv python=3.10 pip`

3. Finally, you activate the virtual environment with:

`conda activate maeserEnv`

and you deactivate it with:

`conda deactivate`

Anything you "pip install" once the environment has been activated will be installed into the environment rather than system-wide.

## Step 2: Install Maeser Into your Virtual Environment

Next, after activating your virtual environment, install maeser:

```bash
pip install Maeser
```

That is it - Maeser is now installed in your environment.

## Step 3: Clone Maeser Onto Your Machine (optional)

The Maeser github repo contains an example directory with a collection of sample uses of Maeser. You will likely want use those examples as your starting point. You can either go to github and copy that directory down or you can simply clone the github repo onto your machine.

To clone the repo, you would do the following shell command:

```shell
git clone https://github.com/byu-cpe/Maeser
```

You are now ready to work through the example apps provided with Maeser. To do so, head over to this page: [Maeser Example (with Flask)](flask_example.md).
