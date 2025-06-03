# vtds-core
The core implementation of the vTDS virtual cluster tool.

## Description

The vTDS core is the top-level driving mechanism that uses vTDS layer
implementations and system configuration overlays to construct a
virtual Test and Development System (vTDS) cluster and deploy an
application on that cluster. The vTDS architecture defines a provider
and application independent way to deploy and manage vTDS instances to
support a variety of site and application development activities. The
architecture achieves this by defining a layered model of both
implementation and configuration and allowing layer implementations to
be mixed and matched (with appropriate configuration) as needed by the
user based on the user suplied configuration overlays.

## Getting started with vTDS

This section provides instructions for the vTDS Core part of getting
started with vTDS. It is targeted at vTDS users, so it takes the
simplest path to getting vTDS Core installed and ready to run. Note
that, because of the modular layered architecture of vTDS, the
instructions here do not cover setting up a provider or configuring a
platform, cluster or application layer. These instructions do,
however, bring the reader to the point where the `vtds` command is
installed and can be used to run all of the `vtds` commands against a
stack of mock layer implementations using a the base configuration of
each mock layer as the minimal configuration. This should allow
validation that the vTDS Core has been properly installed and a chance
to become familiar with the Core configuration and configuration
overlays.

Please also note that vTDS has been tested on macOS and Linux
systems. It has not been tested on Windows. While Python best
practices have been followed to allow it to work on Windows, at
present, using it there is not recommended.

### Python and a Virtual Environment

To use vTDS you will need to have installed an up-to-date
[Python3](https://www.python.org/downloads/). Installing Python3
varies from platform to platform, so this guide does not cover Python installation.

Once Python3 is installed, you will need a Python Virtual Environment, 'venv',
from which to install and run the vTDS Core. To set this up,
pick file system path to the directory where you want to place your
virtual environment and create it using the `python3 -m venv`
command. For example, to place your virtual environment in your home
directory under a `venv` directory use the following:

```
$ python3 -m venv ~/venv
```

Once you have a virtual environment created, activate it so you can
install and run vTDS. Continuing with the example, here is what you
would do (from `bash` or a similar shell):

```
$ source ~/venv/bin/activate
```

Do this in any shell window you want to run inside the virtual
envirnoment. To leave the virtual environment, the command is
`deactivate`.

### Installing vTDS Core

The next step is to install the vTDS Core in your virtual
environment. Continuing with the above example, assuming you have
activated the virtual environment in your shell, simply

```
$ pip install vtds-core
```

### Running vTDS

Now you are ready to make a trial run of vTDS to make sure you have
properly installed `vtds-core`. This will be a mock run of the `vtds`
commands using the unmodified base configurations from the mock layer
implementations.

#### The vTDS Cluster Directory

A vTDS system is deployed from a directory containing an optional vTDS
Core Configuration file and a vTDS generated build tree. The minimum
directory is simply an empty directory from which you will run your
`vtds` commands. After you run the first `vtds` command in that
directory it will contain a directory called `vtds-build` which
contains vTDS generated content pertaining to your cluster. If you
manage more than one cluster, simply create more directories.

For the sake of continuing the example, make a directory called
`~/myvtds` and chdir to it:

```
$ mkdir ~/myvtds
$ chdir ~/myvtds
```

From there you can run `vtds` commands. Since there is no Core
Configuration file present, the base Core Configuration will be used
which pulls in mock layer implementations and uses only the base
configurations from those mock layer implementations.

#### The vTDS Core Configuration

There are several ways to specify the vTDS Core Configuration, but the
simplest is through a file called `config.yaml` in your vTDS Cluster
Directory. In the absence of a vTDS Core Configuration, the default
Core Configuration will be used, which will load mock layer
implementations for the Provider, Platform, Cluster and Application
layers and use their base (default) configurations to allow them to
run. In order to avoid getting into the details of layers other than
the vTDS Core, the following example commands use this default
configuration.

To see more on vTDS Configurations, including canned core and layer
configurations for various system types, visit the
[vtds-configs](https://github.com/Cray-HPE/vtds-configs)
GitHub repository.

To use a core configuration from that repository, just clone the
repository and copy the core configuration you want into your vTDS
Cluster Directory as `config.yaml`. For example:

```
$ git clone git@github.com:Cray-HPE/vtds-configs.git /tmp/vtds-configs
Cloning into '/tmp/vtds-configs'...
remote: Enumerating objects: 389, done.
remote: Counting objects: 100% (33/33), done.
remote: Compressing objects: 100% (23/23), done.
remote: Total 389 (delta 15), reused 13 (delta 9), pack-reused 356 (from 1)
Receiving objects: 100% (389/389), 57.42 KiB | 980.00 KiB/s, done.
Resolving deltas: 100% (186/186), done.
$ cp /tmp/vtds-configs/core-configs/vtds-mock.yaml ~/myvtds/config.yaml 

```

There are basic core configuration files for a wide variety of vTDS systems in
[vtds-configs](https://github.com/Cray-HPE/vtds-configs).

#### The `vtds validate` Command

The `vtds validate` command validates the configuration constructed
based on the Core Configuration. In this case, this is the set of mock
layer implementation base configurations. In the mock layers, output
is generated for each layer showing that it ran.

```
myvtds $ vtds validate
Preparing vtds-provider-mock
Preparing vtds-platform-mock
Preparing vtds-application-mock
Validating vtds-provider-mock
Validating vtds-platform-mock
INFO: Validating vtds-cluster-mock
Validating vtds-application-mock
```

#### The `vtds deploy` Command

The `vtds deploy` command deploys the cluster based on the Core
Configuration. Again, the mock settings will be used, so, in this
case, it will simply print out messages indicating that it ran in each
layer.

```
$ vtds deploy
Preparing vtds-provider-mock
Preparing vtds-platform-mock
Preparing vtds-application-mock
Validating vtds-provider-mock
Validating vtds-platform-mock
INFO: Validating vtds-cluster-mock
Validating vtds-application-mock
Deploying vtds-provider-mock
Deploying vtds-platform-mock
INFO: deploying vtds-cluster-mock
Deploying vtds-application-mock
```

#### The `vtds show_config` Command

The `vtds show_config` command shows the configuration being used to
construct the cluster. This allows you to review what your final
configuration contains to diagnose configuration issues or help you
see what you have done by changing a configuration overlay.

```
$ vtds show_config
application:
  nodes: {}
cluster:
  host_blade_network:
    address_families:
      ipv4:
        cidr: 10.234.0.0/16
        family: AF_INET
    blade_interconnect: mock_interconnect
    delete: false
    ...
```

#### The `vtds base_config` Command

The `vtds base_config` command shows the base (default) configuration
provided by the layer implementations you have chosen for your vTDS
stack. This is an annotated and complete set of configuration settings
that will be used if you do not override them in a subsequent
configuration. This is provided to help with designing new
configurations from scratch and with finding specific tunings to make
your vTDS deployments serve your needs better.

NOTE: In order to preserve annotations in the base configurations,
this command simply dumps out a concatenation of the base
configuration files from each layer implementation, so there will be
multiple copyright notices embedded in the output. You can ignore
these.

```
$ vtds base_config
#
# MIT License
#
<skip>
provider:
  blade_interconnects:
    mock_interconnect:
      network_name: mock-interconnect
      ipv4_cidr: 10.255.0.0/16
  virtual_blades:
    mock_blade:
      count: 3
      hostnames:
        - mock-001
        - mock-002
        - mock-003
    ...
```

### Other Layers

Your core configuration file will determine which layer
implementations you are using to build your vTDS systems. Different
layer implementations will have different setup needs on the system
where vTDS is run. Those are spelled out in the README.md files in
the repositories for each layer implementation.

The following is a list of some available vTDS Layer
Implementations. It is not comprehensive, but these can be used to
construct a vTDS stack and deploy a vTDS Cluster. They can also be
examined to find the installation requirements for these layer
implementations.

- Provider Layer Implementations
  - [Mock Provider Layer](https://github.com/Cray-HPE/vtds-provider-mock)
  - [GCP Provider Layer](https://github.com/Cray-HPE/vtds-provider-gcp)
- Platform Layer Implementations
  - [Mock Platform Layer](https://github.com/Cray-HPE/vtds-platform-mock)
  - [Ubuntu Platform Layer](https://github.com/Cray-HPE/vtds-platform-ubuntu)
- Cluster Layer Implementations
  - [Mock Cluster Layer](https://github.com/Cray-HPE/vtds-cluster-mock)
  - [KVM Cluster Layer](https://github.com/Cray-HPE/vtds-cluster-kvm)
- Application Layer Implementations
  - [Mock Application Layer](https://github.com/Cray-HPE/vtds-application-mock)
  - [OpenCHAMI on vTDS Application layer](https://github.com/Cray-HPE/vtds-application-openchami)

## Brief vTDS Architecture Overview

The layers of the vTDS architecture are:

* Provider
* Platform
* Cluster
* Application

The Provider layer defines the resources that are available from a
given hosting provider (for example, Google Cloud Platform or
GreenLake(r)) on which the vTDS cluster is to be deployed. This
includes things like customer billing information, project
information, including naming within the provider's name space, and
and provider level network (Blade Interconnect) and host (Virtual
Blade) information. This creates the basic topology of the platform on
which the vTDS system will be built.

The Platform layer configures and populates the environment on
Virtual Blades to support the cluster and applicaiton layers. It is
primarily concerned with Virtual Blade OS specific installation of
supporting services and packages and configuration of the Virtual
Blade OS.

The Cluster layer defines the vTDS cluster. It defines and
instantiates Virtual Nodes on their respective Virtual Blades and
defines and constructs Virtual Networks connecting the Virtual Nodes
according to the cluster network topology in the Cluster layer
configuration.

The Application layer defines operations and configuration needed to
set up an environment specifically tailored to the application to be
installed on the cluster. The Application layer also installs and
starts the application.

Layers higher in the architecture can reference and manipulate
resources defined lower in the architecture through strict layer APIs,
one for each layer, which are invariant across layer
implementations. Each layer defines abstract names for Layer API
objects that permit lower layer configuration objects to be referenced
within that layer's API by a higher layer. This permits a complete
system configuration to be constructed layer by layer to meet the
specific needs of a given application and then ported to, for example,
a different provider, simply by replacing the provider layer
configuration and leaving the other layer configurations unchanged.

## The vTDS Core

The vTDS Core has two functions. First, it constructs the stack of
layer implementaitons used to manage a particular vTDS and a vTDS
Configuration that matches the vTDS to be managed. These two
activities are driven by the Core Configuration which specifies the
set of Layer implementations to assemble and the list of configuration
overlay sources (in the order they are to be applied) used to compose
the final vTDS Configuration.

An example core configuration can be found [here](https://github.com/Cray-HPE/vtds-configs/blob/main/core-configs/vtds-mock.yaml).

Once the stack and the configuration have been constructed, the vTDS
Core drives all actions into the stack. The available actions are:

- validate
- deploy
- remove
- show_config
- base_config

The `validate` action runs a validation pass over the final vTDS
Configuration. The `deploy` action causes the vTDS cluster to be
deployed. The `remove` action tears down the vTDS cluster, releasing
all provider resources used by the cluster. The `show_config` action
collates the final vTDS Configuration an prints it on standard
output. This allows the user to see exactly what configuration is
being used for the vTDS cluster. The `base_config` action displays the
base configuration for all of the selected layer configurations, along
with annotations to help designers of new vTDS clusters develop their
configurations.

## The Public Canned Configurations Repository

The configuration mechanism for vTDS lends itself to using canned vTDS
Configuration overlays to construct a vTDS Configuration. The [vTDS
Configuration Repository](https://github.com/Cray-HPE/vtds-configs) is
a public repository containing potentially useful canned vTDS Core
Configurations and Configuration Overlays. These can be used to form
the basis of vTDS Configurations that are then tweaked using private
overlays to construct a final vTDS Configuration for a particular
purpose.
