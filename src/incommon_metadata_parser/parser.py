import logging

from defusedxml.lxml import fromstring
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class RequestedAttribute(object):
    def __init__(self, friendly_name, name, name_format, is_required):
        self.friendly_name = friendly_name
        self.name = name
        self.name_format = name_format
        self.is_required = is_required


class AttributeConsumingService(object):
    def __init__(self, requested_attributes):
        self.requested_attributes = requested_attributes


class ServiceProvider(object):
    def __init__(self, entity_id, display_name, attribute_consuming_services):
        self.entity_id = entity_id
        self.display_name = display_name
        self.attribute_consuming_services = attribute_consuming_services


class MetadataParser(object):
    ENTITY_DESCRIPTOR_XPATH = '//md:EntityDescriptor'
    SP_DESCRIPTOR_XPATH = './md:SPSSODescriptor'
    ENTITY_ID_ATTRIBUTE = 'entityID'
    DISPLAY_NAME_XPATH = './md:Extensions/mdui:UIInfo/mdui:DisplayName'
    ATTRIBUTE_CONSUMING_SERVICE_XPATH = './md:AttributeConsumingService'

    REQUESTED_ATTRIBUTE_XPATH = './md:RequestedAttribute'
    FRIENDLY_NAME_ATTRIBUTE = 'FriendlyName'
    NAME_ATTRIBUTE = 'FriendlyName'
    NAME_FORMAT_ATTRIBUTE = 'NameFormat'
    IS_REQUIRED_ATTRIBUTE = 'isRequired'

    def __init__(self):
        self._logger = logging.getLogger(__name__)

        OneLogin_Saml2_Constants.NS_PREFIX_MDUI = 'mdui'
        OneLogin_Saml2_Constants.NS_MDUI = 'urn:oasis:names:tc:SAML:metadata:ui'
        OneLogin_Saml2_Constants.NSMAP[OneLogin_Saml2_Constants.NS_PREFIX_MDUI] = OneLogin_Saml2_Constants.NS_MDUI

    def _convert_string_to_xml_dom(self, metadata):
        self._logger.info('Started converting metadata string into XML DOM')

        metadata_dom = fromstring(metadata, forbid_dtd=True)

        self._logger.info('Finished converting metadata string into XML DOM')

        return metadata_dom

    def _parse_metadata_dom(self, metadata_dom):
        entity_descriptor_nodes = OneLogin_Saml2_Utils.query(metadata_dom, self.ENTITY_DESCRIPTOR_XPATH)
        sps = []

        for entity_descriptor_node in entity_descriptor_nodes:
            sp_entity_id = entity_descriptor_node.get(self.ENTITY_ID_ATTRIBUTE, None)
            sp_descriptor_nodes = OneLogin_Saml2_Utils.query(entity_descriptor_node, self.SP_DESCRIPTOR_XPATH)

            for sp_descriptor_node in sp_descriptor_nodes:
                display_name_node = OneLogin_Saml2_Utils.query(sp_descriptor_node, self.DISPLAY_NAME_XPATH)

                if not display_name_node:
                    continue

                display_name = display_name_node[0].text

                attribute_consuming_service_nodes = OneLogin_Saml2_Utils.query(
                    sp_descriptor_node, self.ATTRIBUTE_CONSUMING_SERVICE_XPATH)

                attribute_consuming_services = []

                for attribute_consuming_service_node in attribute_consuming_service_nodes:
                    requested_attributes = []
                    requested_attribute_nodes = OneLogin_Saml2_Utils.query(
                        attribute_consuming_service_node, self.REQUESTED_ATTRIBUTE_XPATH)

                    for requested_attribute_node in requested_attribute_nodes:
                        friendly_name = requested_attribute_node.get(self.FRIENDLY_NAME_ATTRIBUTE, '')
                        name = requested_attribute_node.get(self.NAME_ATTRIBUTE, '')
                        name_format = requested_attribute_node.get(self.NAME_FORMAT_ATTRIBUTE, '')
                        is_required = requested_attribute_node.get(self.IS_REQUIRED_ATTRIBUTE, False)
                        requested_attribute = RequestedAttribute(
                            friendly_name,
                            name,
                            name_format,
                            is_required
                        )

                        requested_attributes.append(requested_attribute)

                    attribute_consuming_service = AttributeConsumingService(
                        requested_attributes
                    )

                    attribute_consuming_services.append(attribute_consuming_service)

                idp = ServiceProvider(
                    sp_entity_id,
                    display_name,
                    attribute_consuming_services
                )

                sps.append(idp)

        return sps

    def parse(self, metadata):
        self._logger.info('Started fetching IdPs from InCommon Metadata Service')

        in_common_idps = []

        try:
            metadata_dom = self._convert_string_to_xml_dom(metadata)

            for idp in self._parse_metadata_dom(metadata_dom):
                in_common_idps.append(idp)
        except:
            self._logger.exception(
                'An unexpected exception occurred during fetching IdP metadata from InCommon Metadata service')
            raise

        self._logger.info('Successfully fetched {0} IdPs from In Common Metadata Service'.format(len(in_common_idps)))

        idps = in_common_idps

        return idps
