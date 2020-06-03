import logging
import ssl
import urllib2

from defusedxml.lxml import fromstring
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class MetadataLoader(object):
    IN_COMMON_METADATA_SERVICE_URL = 'http://md.incommon.org/InCommon/InCommon-metadata.xml'

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def load_metadata(self, url, validate_cert=True):
        """
        Gets the metadata XML from the provided URL

        :param url: Url where the XML of the Identity Provider Metadata is published.
        :type url: string

        :param validate_cert: If the url uses https schema, that flag enables or not the verification of the associated certificate.
        :type validate_cert: bool

        :returns: metadata XML
        :rtype: string
        """

        self._logger.info('Start loading metadata from {0}'.format(self.IN_COMMON_METADATA_SERVICE_URL))

        valid = False
        if validate_cert:
            response = urllib2.urlopen(url)
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib2.urlopen(url, context=ctx)
        xml = response.read()

        if xml:
            try:
                dom = fromstring(xml, forbid_dtd=True)
                sp_descriptor_nodes = OneLogin_Saml2_Utils.query(dom, '//md:SPSSODescriptor')
                if sp_descriptor_nodes:
                    valid = True
            except Exception:
                pass

        if not valid:
            raise Exception('Not valid IdP XML found from URL: %s' % url)

        self._logger.info('Finished loading metadata from {0}'.format(self.IN_COMMON_METADATA_SERVICE_URL))

        return xml
