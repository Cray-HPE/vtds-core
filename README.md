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

### vtds-core

To use vTDS you will need to have installed an up-to-date Python3 and
you will want to have set up a Python virtual environment using
```
python3 -m venv <path to your venv>
```
and activated that virtual environment using
```
source <path to your venv>/bin/activate
```

Once you have that in place, you will need to install `vtds-base` and
`vtds-core` as Python modules in your virtual environment. You can
clone [vtds-base](https://github.com/Cray-HPE/vtds-base) and install it using
```
pip install .
```
from within the clone directory.

Assuming you have this
([vtds-core](https://github.com/Cray-HPE/vtds-core)) repository cloned
already, the easiest way to install `vtds-core` is to run
```
pip install .
```
in the clone directory.

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
  - [FSM Connectivity Demo Application Layer](https://github.com/Cray-HPE/vtds-application-demo)

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
network and provider level network and host information, including
network and node classes, used to by higher layers to build the final
cluster. The provider layer also contains the code and to set up
Virtual Blades and Blade Interconnect networks on the specific
provider. This creates the topology of the platform on which the vTDS
system will be built.

The Platform layer configures and populates the environment on the
virtual blades to support the cluster and applicaiton layers. It is
primarily concerned with Virtual Blade OS specific installation of
supporting services and packages and configuration of the Virtual
Blade OS.

The Cluster layer defines the vTDS cluster. It instantiates Virtual
Nodes on their respective Virtual Blades and builds Virtual Networks
to interconnect the Virtual Nodes according to the cluster network
topology.

The Application layer defines operations and configuration needed to
set up an environment specifically tailored to the application to be
installed on the cluster. The Application layer also installs and
starts the application.

Layers higher in the architecture can reference and manipulate
resources defined lower in the architecture through layer APIs, one
for each layer, which are invariant across layer implementations. Each
layer defines abstract names for Layer API objects that permit lower
layer configuration objects to be referenced within that layer's API
by a higher layer. This permits a complete system configuration to be
constructed layer by layer to meet the specific needs of a given
application and then ported to, for example, a different provider,
simply by replacing the provider layer configuration and leaving the
other layer configurations unchanged.

## The vTDS Core

The vTDS Core has two functions. First, it constructs the stack of
layer implementaitons used to manage a particular vTDS and a vTDS
Configuration that matches the vTDS to be managed. These two
activities are driven by the Core Configuration which specifies the
set of Layer implementations to assemble and the list of configuration
overlay sources (in the order they are to be applied) used to compose
the final vTDS Configuration.

An example core configuration can be found [here](https://github.com/Cray-HPE/vtds-configs/blob/9f42e0005c18e0de8de9aa72248252b74c693de4/core-configs/vtds-fsm-connectivity-git-layers.yaml).

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
