from django.test import TestCase
from push_notifications.apns import _apns_send, APNSDataOverflow
from ._mock import mock


class APNSPushPayloadTest(TestCase):
	def test_push_payload(self):
		socket = mock.MagicMock()
		with mock.patch("push_notifications.apns._apns_pack_frame") as p:
			_apns_send(
				"123", "Hello world", badge=1, sound="chime",
				extra={"custom_data": 12345}, expiration=3, socket=socket
			)
			p.assert_called_once_with(
				"123",
				b'{"aps":{"alert":"Hello world","badge":1,"sound":"chime"},"custom_data":12345}',
				0, 3, 10)

	def test_push_payload_with_thread_id(self):
		socket = mock.MagicMock()
		with mock.patch("push_notifications.apns._apns_pack_frame") as p:
			_apns_send(
				"123", "Hello world", thread_id="565", sound="chime",
				extra={"custom_data": 12345}, expiration=3, socket=socket
			)
			p.assert_called_once_with(
				"123",
				b'{"aps":{"alert":"Hello world","sound":"chime","thread-id":"565"},"custom_data":12345}',
				0, 3, 10)

	def test_push_payload_with_alert_dict(self):
		socket = mock.MagicMock()
		with mock.patch("push_notifications.apns._apns_pack_frame") as p:
			_apns_send(
				"123", alert={'title':'t1', 'body':'b1'}, sound="chime",
				extra={"custom_data": 12345}, expiration=3, socket=socket
			)
			p.assert_called_once_with(
				"123",
				b'{"aps":{"alert":{"body":"b1","title":"t1"},"sound":"chime"},"custom_data":12345}',
				0, 3, 10)

	def test_localised_push_with_empty_body(self):
		socket = mock.MagicMock()
		with mock.patch("push_notifications.apns._apns_pack_frame") as p:
			_apns_send("123", None, loc_key="TEST_LOC_KEY", expiration=3, socket=socket)
			p.assert_called_once_with(
				"123", b'{"aps":{"alert":{"loc-key":"TEST_LOC_KEY"}}}', 0, 3, 10
			)

	def test_using_extra(self):
		socket = mock.MagicMock()
		with mock.patch("push_notifications.apns._apns_pack_frame") as p:
			_apns_send(
				"123", "sample", extra={"foo": "bar"}, identifier=10,
				expiration=30, priority=10, socket=socket
			)
			p.assert_called_once_with("123", b'{"aps":{"alert":"sample"},"foo":"bar"}', 10, 30, 10)

	def test_oversized_payload(self):
		socket = mock.MagicMock()
		with mock.patch("push_notifications.apns._apns_pack_frame") as p:
			self.assertRaises(APNSDataOverflow, _apns_send, "123", "_" * 2049, socket=socket)
			p.assert_has_calls([])
