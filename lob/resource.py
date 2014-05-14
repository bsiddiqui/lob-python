from lob import api_requestor
import json

def lob_format(resp):
  types = {'address': Address}

  if isinstance(resp, list):
    return [lob_format(i) for i in resp]
  elif isinstance(resp, dict) and not isinstance(resp, LobObject):
    resp = resp.copy()
    klass_name = resp.get('object')
    if isinstance(klass_name, basestring):
      klass = types.get(klass_name, LobObject)
    else:
      klass = LobObject
    return klass.construct_from(resp)
  else:
    return resp

class LobObject(dict):

  def __init__(self, id=None, **params):
    super(LobObject, self).__init__()
    if id:
      self['id'] = id

  @classmethod
  def construct_from(cls, values):
    instance = cls(values.get('id'))
    for k, v in values.iteritems():
      instance[k] = lob_format(v)
    return instance

  def __getattr__(self, k):
    try:
      return self[k]
    except KeyError, err:
      raise AttributeError(k)

  def __setattr__(self, k, v):
    self[k] = v

  def __repr__(self):
    ident_parts = [type(self).__name__]

    if isinstance(self.get('object'), basestring):
      ident_parts.append(self.get('object'))

    if isinstance(self.get('id'), basestring):
      ident_parts.append('id=%s' % (self.get('id'),))

    unicode_repr = '<%s at %s> JSON: %s' % (
      ' '.join(ident_parts), hex(id(self)), str(self))

    return unicode_repr

    print ident_parts

  def __str__(self):
    return json.dumps(self, sort_keys=True, indent=2)

class APIResource(LobObject):
  @classmethod
  def retrieve(cls, id, **params):
    requestor = api_requestor.APIRequestor()
    response = requestor.request('get', '%s/%s' % (cls.url, id), params)
    return lob_format(response)

# API Operations
class ListableAPIResource(APIResource):
  @classmethod
  def list(cls, **params):
    requestor = api_requestor.APIRequestor()
    response = requestor.request('get', cls.url, params)
    return lob_format(response['data'])

class DeleteableAPIResource(APIResource):
  @classmethod
  def delete(cls, id):
    requestor = api_requestor.APIRequestor()
    response = requestor.request('delete', '%s/%s' % (cls.url, id))
    return lob_format(response)

class Address(ListableAPIResource, DeleteableAPIResource):
  url = '/addresses'
  pass