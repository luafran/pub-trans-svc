For this project you will need to write a scalable and highly available service that will provide real-time
data of San Francisco’s buses and trains (SF Muni).

You will be required to write your application in Python or Go and use Docker containers.

The containers will be serving an API, which should be stateless and be able to work seamlessly in your highly
available setup. You will need to decide which setup to use.  Make reasonable assumptions, state your
assumptions, and proceed.

The system will be complex enough to require multiple containers. Use a system of your choice to run the
containers (e.g. Docker Compose, Kubernetes, etc).

NextBus provides a real-time data feed that exposes bus and train service information to the public.
The instructions for using the real-time data feed are here:

http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf

Your project will extend and wrap NextBus public XML feed as a RESTful HTTP API with the following
requirements:

* Expose all of the endpoints in the NextBus API
* An endpoint to retrieve the routes that are not running at a specific time. For example, the 6 bus does
not run between 1 AM and 5 AM, so the output of a query for 2 AM should include the 6.
* Two endpoints to retrieve internal statistics about your service:
    * The total number of queries made to each of the endpoints in your API
    * A list of slow requests
* The output can be in either JSON or XML format (or both).
* Do not hurt the NextBus service. The same request should not be made more than once within a 30 second interval.