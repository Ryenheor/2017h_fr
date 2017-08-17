# # things.py
#
# # Let's get this party started!
# import falcon
#
#
# # Falcon follows the REST architectural style, meaning (among
# # other things) that you think in terms of resources and state
# # transitions, which map to HTTP verbs.
# class ThingsResource(object):
#     def on_get(self, req, resp):
#         """Handles GET requests"""
#         resp.status = falcon.HTTP_200  # This is the default status
#         resp.body = ('\nTwo things awe me most, the starry sky '
#                      'above me and the moral law within me.\n'
#                      '\n'
#                      '    ~ Immanuel Kant\n\n')
#
# # falcon.API instances are callable WSGI apps
# app = falcon.API()
#
# # Resources are represented by long-lived class instances
# things = ThingsResource()
#
# # things will handle all requests to the '/things' URL path
# app.add_route('/things', things)

#
# import falcon
# import json
#
# class Resource(object):
#
#     def on_get(self, req, resp):
#         doc = {
#             'images': [
#                 {
#                     'fff': 'jh'
#                 }
#             ]
#         }
#         print("2")
#         # Create a JSON representation of the resource
#         resp.body = json.dumps(doc, ensure_ascii=False)
#
#         # The following line can be omitted because 200 is the default
#         # status returned by the framework, but it is included here to
#         # illustrate how this may be overridden as needed.
#         resp.status = falcon.HTTP_200
#
#
# api = application = falcon.API()
# images = Resource()
# print("1")
# api.add_route('/images', images)