============
Installation
============

How to install?
------------------------------------

Clone RAVEN
++++++++++++++++++++++++++++++++++++
Open a terminal window and cd into the folder where you want to install RAVEN (e.g., projects)

.. code:: bash

    [~]> mkdir projects
    [~]> cd projects
    [~/projects]> git clone https://github.com/idaholab/raven.git
    [~/projects]> cd raven

Install RAVEN Plugins
+++++++++++++++++++++++++++++++++++++++
To register BayCal as a plugin for RAVEN and make its components accessible, run the script

.. code:: bash

  raven/scripts/install_plugins.py -s /abs/path/to/BayCal

To install all officially-supported plugins, the shortcut option `-a` or `--all` can be used:

.. code:: bash

  raven/scripts/install_plugins.py -a

At this stage, RAVEN will import all the plugins within that directory and perform some error checking.

Install RAVEN libraries
++++++++++++++++++++++++++++++++++++++++

.. code:: bash

    cd raven
    ./scripts/establish_conda_env.sh --install


Compiling RAVEN
+++++++++++++++++++++++++++++++++++++++++++

.. code:: bash

    [~/projects/raven]> ./build_raven

In case the RAVEN libraries have been installed without the ```conda``` installation package,
(see install_raven_), RAVEN needs to be built with the following option:

.. code:: bash

    [~/projects/raven]> ./build_raven --skip-conda

Test RAVEN installation
+++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: bash

    [~/projects/raven]> ./run_tests -j2


Using the plugin in RAVEN
+++++++++++++++++++++++++++++++++++++++++++++++++++
Once registered, new external models can be used in RAVEN by using the model subtype defined by
your plugin name. For example, you can access BayCal model in the RAVEN input as

.. code-block:: xml

    <Models>
      ...
      <ExternalModel name='myName' subType='BayCal.LikelihoodModel'>
        ...
      </ExternalModel>
      ...
    </Models>


Issues
++++++++++++++++++++++++++++++++++++++++++++++++++++
Please refer to the following links if there is any issue happening during the installation process.

  #. Install RAVEN_, please refer to install_raven_
  #. Install RAVEN Plugins, i.e., BayCal, please refer to install_raven_plugins_

.. _RAVEN: https://github.com/idaholab/raven
.. _install_raven: https://github.com/idaholab/raven/wiki/installationMain
.. _install_raven_plugins: https://github.com/idaholab/raven/wiki/Plugins
