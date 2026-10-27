import unittest
from fastapi.testclient import TestClient
from mock_api import api

class ApiSimulationTests(unittest.TestCase):
 def setUp(self): self.client=TestClient(api)
 def test_catalog_success_loading_fixture_empty_error(self):
  self.assertEqual(self.client.get('/catalog').status_code,200)
  self.assertEqual(len(self.client.get('/catalog').json()),3)
  self.assertEqual(self.client.get('/catalog?mode=empty').json(),[])
  self.assertEqual(self.client.get('/catalog?mode=error').status_code,503)
 def test_session_headers_and_role_restriction(self):
  student=self.client.post('/session',json={'perfil':'estudante'}).json()['token']
  librarian=self.client.post('/session',json={'perfil':'bibliotecario'}).json()['token']
  self.assertEqual(self.client.get('/session',headers={'X-Demo-Session':student}).status_code,200)
  self.assertEqual(self.client.post('/admin/action',headers={'X-Demo-Session':student}).status_code,403)
  self.assertEqual(self.client.post('/admin/action',headers={'X-Demo-Session':librarian}).status_code,200)
  self.assertEqual(self.client.post('/admin/action').status_code,401)
 def test_request_reservation_and_confirmation(self):
  student='demo-estudante-token'
  self.assertEqual(self.client.post('/loans/request',headers={'X-Demo-Session':student}).status_code,200)
  self.assertEqual(self.client.get('/reservations',headers={'X-Demo-Session':student}).status_code,200)
  self.assertEqual(self.client.post('/loans/confirm',headers={'X-Demo-Session':student}).status_code,403)
  self.assertEqual(self.client.post('/loans/confirm',headers={'X-Demo-Session':'demo-bibliotecario-token'}).status_code,200)

if __name__=='__main__': unittest.main()
