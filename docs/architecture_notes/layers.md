Provider

   The Provider Layer is the foundation layer of the vTDS system.

   The Provider Layer presents Virtual Blades and Blade Interconnects to
   the higher layers as named objects that are resolvable within the
   Provider Layer and can be used for API operations.

   The configuration of the Provider Layer determines what flavor of
   operating system is running on the Virtual Blades. This, in turn
   dictates the choice of Platform Layers that are compatible with the
   provider layer.

   The Provider Layer configuration may contain other layer
   implementation specific configuration that includes, for example,
   billing accounts, project names, organization-wide settings and so
   forth. Those are not accessible at the Provider Layer API.

   The Provider Layer implements all logic required to deploy this
   foundation on the kind of provider it has been implemented
   for. Examples of a provider are GCP, OpenStack, Physical
   Hardware, GreenLake, and so forth.

Platform

   The Platform Layer constructs a specific flavor of virtualized
   platform that abstracts the concept of platform on top of provider
   resources. It expects Virtual Blades and Blade Interconnects to be
   defined and set up by the Provider Layer and uses those for the
   following:

   - Virtual Networks (layer 2 implementation) overlaid onto Blade
     Interconnects

   - Virtual Network Interfaces on Virtual Blades (available for
     eventual use by Virtual Nodes)

   - Virtual Blade level services as appropriate, possible examples include:
     + Hypervisor / VM Hosting Services
     + Virtual BMC
     + DHCP Server
     + DNS Server
     + Boot Server
     + Cloud Init Server

   The Platform Layer exports named objects representing these elements
   that are then available to configuration of the layers above the
   Platform Layer. The Platform Layer presents an API that permits
   interaction with those objects as well.

   The Platform Layer configuration is dependent on the flavor of
   operating system running on the Virtual Blades, so different Provider
   Layer implementations exist to support different flavors of Virtual
   Blade operating system.

Cluster

   The Cluster Layer constructs a Cluster of Nodes and their respective
   layer 3 relationships using the resources of the Platform and
   Provider Layers. It uses Hypervisor / VM Hosting services provided by
   the Platform Layer through the Platform Layer API to manage Virtual
   Nodes in the cluster. It uses Virtual Networks and Virtual Network
   innterfaces provided by the Platform Layer to construct Layer 3
   connectivity between Virtual Nodes within the network toplogy defined
   by the Platform Layer.

   The choice of Cluster Layer is primarily determined by the choice of
   the the Hypervisor / VM Hosting Service configured or defined by the
   Platform Layer [NOTE: revisit this, we may be able to abstract
   everything we need from the hosting behind the Platform Layer API].

Application

   The Application Layer is responsible for deploying the application on
   the cluster constructed by the Cluster Layer. Since the definition of
   an application is arbitrary, the application layer provides whatever
   shims are needed to deploy and run the application along with
   execution of the application deployment procedures themselves to the
   extent desired. Some applications, once deployed may obviate the need
   for certain services at the Platform Layer, in which case the
   Application Layer will take care of transitioning from Platform Layer
   provided services to application provided equivalent services through
   the Platform Layer API.
