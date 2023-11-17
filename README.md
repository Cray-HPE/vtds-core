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
cluster. The Platform layer defines the topology of the platform on
which a cluster will be built. This includes things like the number
and classes of hosts, referred to as Virtual Blades, the number and
classes of external networks and the number of classes of networks
used to interconnect host systems inside the cluster, referred to as
Blade Interconnect Networks. The Cluster layer defines the topology of
the virtual cluster itself. This includes things like the specific
cluster node configurations and Virtual Blade bindings and the
configurations of the Virtual Node Interconnect networks that connect
nodes in the cluster together and their Blade Interconnect Network
bindings. The Application layer defines configuration specific to the
application to be installed on the cluster.

Layers higher in the architecture can reference and manipulate
resources defined lower in the architecture through layer APIs, one
for each layer, which are invariant across layer implementations. Each
layer defines abstract tags within its configuration that permit lower
layer configuration items to be referenced within that layer's API by
a higher layer. This permits a complete system configuration to be
constructed layer by layer to meet the specific needs of a given
application and then ported to, say, a different provider, simply by
replacing the provider layer configuration and leaving the other layer
configurations unchanged.

## The vTDS Core

The vTDS core drives all actions on on a given vTDS system. To do
this, the vTDS requires a (set of) user supplied System Configuration
Overlay(s) each of which is a YAML file containing the configuration
changes to be applied on top of the base configuration of each layer
of the vTDS architecture. The structure of the system configuration
permits all of the layers to be configured in a single overlay. By
specifying multiple overlays, it is possible to keep common
configuration used across many systems in a common set of overlays and
re-use those overlay for every system that shares that common
configuration while putting only system specific settings in an
overlay specific to a single vTDS instance. The list of configuration
overlays used to construct a given vTDS system can be specified within
a system configuration overlay itself, in which case the elements of
that list are added, in order of discovery ignoring already discovered
overlays to avoid circular references, to any list of already
specified overlays. Any number of system configuration overlays can
also be specified on the command line, in which case, these are
scanned for included overlays in the order in which they occur on the
command line. Overlays are merged in reverse order from which they
were discovered, so overlays discovered first will override overlays
discovered later. This way a system specific overlay can pull in less
specific overlays and be sure of having the final say on the ultimate
system configuration.

The vTDS core constructs its system configuration roughly as follows:

1) Iteratively identify and gather all of the configuration overlays that
   compose the system configuration
2) Merge the configuration overlays in reverse order and create a master
   configuration overlay
3) Identify and gather the correct layer implementations based on the master
   configuration overlay
4) Merge the base configurations from the layer implementations and create
   a master base configuration
5) Merge the master configuration overlay onto the master base configuration
   to create a system configuration

Using the resulting sysem configuration and the gathered layer
implemenations, the vTDS core executes pre-defined actions using layer
APIs to drive deployment, validation, update and tear-down of the vTDS
cluster and its application as directed by the user.
