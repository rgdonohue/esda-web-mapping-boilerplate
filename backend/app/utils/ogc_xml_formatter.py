import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional
from xml.dom import minidom

from app.models.ogc_models import (
    OGCServiceType,
    OGCVersion,
    WFSGetCapabilitiesResponse,
    WMSGetCapabilitiesResponse,
)
from app.utils.enhanced_logging import get_logger

logger = get_logger(__name__)


def prettify_xml(elem: ET.Element) -> str:
    """Return a pretty-printed XML string for the Element.

    Args:
        elem: XML Element to prettify

    Returns:
        Pretty-printed XML string
    """
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def format_wms_capabilities_xml(capabilities: WMSGetCapabilitiesResponse) -> str:
    """Format WMS GetCapabilities response as XML.

    Args:
        capabilities: WMS GetCapabilities response object

    Returns:
        XML string representation of the capabilities
    """
    # Create root element
    wms = ET.Element("WMS_Capabilities")
    wms.set("version", capabilities.version)
    wms.set("xmlns", "http://www.opengis.net/wms")
    wms.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    wms.set(
        "xsi:schemaLocation",
        "http://www.opengis.net/wms http://schemas.opengis.net/wms/1.3.0/capabilities_1_3_0.xsd",
    )

    # Service section
    service = ET.SubElement(wms, "Service")

    # Service metadata
    name = ET.SubElement(service, "Name")
    name.text = "WMS"

    title = ET.SubElement(service, "Title")
    title.text = capabilities.service_metadata.get("title", "WMS Service")

    abstract = ET.SubElement(service, "Abstract")
    abstract.text = capabilities.service_metadata.get("abstract", "")

    # Contact information
    contact_info = capabilities.service_metadata.get("contact_information", {})
    if contact_info:
        contact = ET.SubElement(service, "ContactInformation")

        person_primary = contact_info.get("person_primary", {})
        if person_primary:
            contact_person = ET.SubElement(contact, "ContactPersonPrimary")

            person_name = ET.SubElement(contact_person, "ContactPerson")
            person_name.text = person_primary.get("person_name", "")

            org_name = ET.SubElement(contact_person, "ContactOrganization")
            org_name.text = person_primary.get("organization", "")

        contact_email = ET.SubElement(contact, "ContactElectronicMailAddress")
        contact_email.text = contact_info.get("contact_email", "")

    # Capability section
    capability = ET.SubElement(wms, "Capability")

    # Request section
    request = ET.SubElement(capability, "Request")

    # GetCapabilities
    get_capabilities = ET.SubElement(request, "GetCapabilities")
    get_capabilities_format = ET.SubElement(get_capabilities, "Format")
    get_capabilities_format.text = "text/xml"

    get_capabilities_dcp = ET.SubElement(get_capabilities, "DCPType")
    get_capabilities_http = ET.SubElement(get_capabilities_dcp, "HTTP")
    get_capabilities_get = ET.SubElement(get_capabilities_http, "Get")
    get_capabilities_get_url = ET.SubElement(get_capabilities_get, "OnlineResource")
    get_capabilities_get_url.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    get_capabilities_get_url.set("xlink:type", "simple")
    get_capabilities_get_url.set("xlink:href", "http://example.com/api/v1/ogc/wms")

    # GetMap
    get_map = ET.SubElement(request, "GetMap")

    for format_name in capabilities.formats:
        get_map_format = ET.SubElement(get_map, "Format")
        get_map_format.text = format_name

    get_map_dcp = ET.SubElement(get_map, "DCPType")
    get_map_http = ET.SubElement(get_map_dcp, "HTTP")
    get_map_get = ET.SubElement(get_map_http, "Get")
    get_map_get_url = ET.SubElement(get_map_get, "OnlineResource")
    get_map_get_url.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    get_map_get_url.set("xlink:type", "simple")
    get_map_get_url.set("xlink:href", "http://example.com/api/v1/ogc/wms/map")

    # Layer section
    layer = ET.SubElement(capability, "Layer")

    root_layer_title = ET.SubElement(layer, "Title")
    root_layer_title.text = "Available Layers"

    # CRS
    for crs_name in capabilities.crs:
        crs_elem = ET.SubElement(layer, "CRS")
        crs_elem.text = crs_name

    # Child layers
    for layer_info in capabilities.layers:
        child_layer = ET.SubElement(layer, "Layer")
        child_layer.set("queryable", "1" if layer_info.get("queryable", False) else "0")

        child_name = ET.SubElement(child_layer, "Name")
        child_name.text = layer_info.get("name", "")

        child_title = ET.SubElement(child_layer, "Title")
        child_title.text = layer_info.get("title", "")

        child_abstract = ET.SubElement(child_layer, "Abstract")
        child_abstract.text = layer_info.get("abstract", "")

        # Layer CRS
        for crs_name in layer_info.get("crs", []):
            child_crs = ET.SubElement(child_layer, "CRS")
            child_crs.text = crs_name

        # Bounding box
        bbox = layer_info.get("bbox", [])
        if len(bbox) == 4:
            ex_bbox = ET.SubElement(child_layer, "EX_GeographicBoundingBox")

            west = ET.SubElement(ex_bbox, "westBoundLongitude")
            west.text = str(bbox[0])

            south = ET.SubElement(ex_bbox, "southBoundLatitude")
            south.text = str(bbox[1])

            east = ET.SubElement(ex_bbox, "eastBoundLongitude")
            east.text = str(bbox[2])

            north = ET.SubElement(ex_bbox, "northBoundLatitude")
            north.text = str(bbox[3])

        # Styles
        for style_name in layer_info.get("styles", []):
            style = ET.SubElement(child_layer, "Style")

            style_name_elem = ET.SubElement(style, "Name")
            style_name_elem.text = style_name

            style_title = ET.SubElement(style, "Title")
            style_title.text = style_name.capitalize()

    return prettify_xml(wms)


def format_wfs_capabilities_xml(capabilities: WFSGetCapabilitiesResponse) -> str:
    """Format WFS GetCapabilities response as XML.

    Args:
        capabilities: WFS GetCapabilities response object

    Returns:
        XML string representation of the capabilities
    """
    # Create root element
    wfs = ET.Element("WFS_Capabilities")
    wfs.set("version", capabilities.version)
    wfs.set("xmlns", "http://www.opengis.net/wfs/2.0")
    wfs.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    wfs.set(
        "xsi:schemaLocation",
        "http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd",
    )

    # Service Identification
    service_id = ET.SubElement(wfs, "ServiceIdentification")

    title = ET.SubElement(service_id, "Title")
    title.text = capabilities.service_metadata.get("title", "WFS Service")

    abstract = ET.SubElement(service_id, "Abstract")
    abstract.text = capabilities.service_metadata.get("abstract", "")

    keywords = capabilities.service_metadata.get("keywords", [])
    if keywords:
        keywords_elem = ET.SubElement(service_id, "Keywords")
        for keyword in keywords:
            keyword_elem = ET.SubElement(keywords_elem, "Keyword")
            keyword_elem.text = keyword

    service_type = ET.SubElement(service_id, "ServiceType")
    service_type.text = "WFS"

    service_type_version = ET.SubElement(service_id, "ServiceTypeVersion")
    service_type_version.text = capabilities.version

    # Service Provider
    service_provider = ET.SubElement(wfs, "ServiceProvider")

    provider_name = ET.SubElement(service_provider, "ProviderName")
    provider_name.text = "ESDA Web Mapping"

    contact_info = capabilities.service_metadata.get("contact_information", {})
    if contact_info:
        service_contact = ET.SubElement(service_provider, "ServiceContact")

        person_primary = contact_info.get("person_primary", {})
        if person_primary:
            individual_name = ET.SubElement(service_contact, "IndividualName")
            individual_name.text = person_primary.get("person_name", "")

            position_name = ET.SubElement(service_contact, "PositionName")
            position_name.text = "Administrator"

            contact_info_elem = ET.SubElement(service_contact, "ContactInfo")

            address = ET.SubElement(contact_info_elem, "Address")

            electronic_mail_address = ET.SubElement(address, "ElectronicMailAddress")
            electronic_mail_address.text = contact_info.get("contact_email", "")

    # Operations Metadata
    operations_metadata = ET.SubElement(wfs, "OperationsMetadata")

    # GetCapabilities operation
    get_capabilities_op = ET.SubElement(operations_metadata, "Operation")
    get_capabilities_op.set("name", "GetCapabilities")

    get_capabilities_dcp = ET.SubElement(get_capabilities_op, "DCP")
    get_capabilities_http = ET.SubElement(get_capabilities_dcp, "HTTP")
    get_capabilities_get = ET.SubElement(get_capabilities_http, "Get")
    get_capabilities_get.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    get_capabilities_get.set("xlink:href", "http://example.com/api/v1/ogc/wfs")

    # GetFeature operation
    get_feature_op = ET.SubElement(operations_metadata, "Operation")
    get_feature_op.set("name", "GetFeature")

    get_feature_dcp = ET.SubElement(get_feature_op, "DCP")
    get_feature_http = ET.SubElement(get_feature_dcp, "HTTP")
    get_feature_get = ET.SubElement(get_feature_http, "Get")
    get_feature_get.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    get_feature_get.set("xlink:href", "http://example.com/api/v1/ogc/wfs/feature")

    # Parameter: outputFormat
    output_format_param = ET.SubElement(operations_metadata, "Parameter")
    output_format_param.set("name", "outputFormat")

    for format_name in capabilities.formats:
        output_format_value = ET.SubElement(output_format_param, "AllowedValues")
        output_format_value_elem = ET.SubElement(output_format_value, "Value")
        output_format_value_elem.text = format_name

    # FeatureTypeList
    feature_type_list = ET.SubElement(wfs, "FeatureTypeList")

    for feature_type in capabilities.feature_types:
        feature_type_elem = ET.SubElement(feature_type_list, "FeatureType")

        name = ET.SubElement(feature_type_elem, "Name")
        name.text = feature_type.get("name", "")

        title = ET.SubElement(feature_type_elem, "Title")
        title.text = feature_type.get("title", "")

        abstract = ET.SubElement(feature_type_elem, "Abstract")
        abstract.text = feature_type.get("abstract", "")

        # Keywords
        keywords = feature_type.get("keywords", [])
        if keywords:
            keywords_elem = ET.SubElement(feature_type_elem, "Keywords")
            for keyword in keywords:
                keyword_elem = ET.SubElement(keywords_elem, "Keyword")
                keyword_elem.text = keyword

        # Default CRS
        default_crs = ET.SubElement(feature_type_elem, "DefaultCRS")
        default_crs.text = (
            feature_type.get("crs", [])[0] if feature_type.get("crs", []) else "EPSG:4326"
        )

        # Other CRS
        for crs_name in feature_type.get("crs", [])[1:]:
            other_crs = ET.SubElement(feature_type_elem, "OtherCRS")
            other_crs.text = crs_name

        # Bounding box
        bbox = feature_type.get("bbox", [])
        if len(bbox) == 4:
            wgs84_bbox = ET.SubElement(feature_type_elem, "WGS84BoundingBox")
            wgs84_bbox.set("xmlns", "http://www.opengis.net/ows/1.1")

            lower_corner = ET.SubElement(wgs84_bbox, "LowerCorner")
            lower_corner.text = f"{bbox[0]} {bbox[1]}"

            upper_corner = ET.SubElement(wgs84_bbox, "UpperCorner")
            upper_corner.text = f"{bbox[2]} {bbox[3]}"

    return prettify_xml(wfs)


def format_ogc_exception_xml(
    exception_code: str, exception_text: str, locator: Optional[str] = None
) -> str:
    """Format OGC Exception as XML.

    Args:
        exception_code: Exception code
        exception_text: Exception text
        locator: Optional locator

    Returns:
        XML string representation of the exception
    """
    # Create root element
    service_exception_report = ET.Element("ServiceExceptionReport")
    service_exception_report.set("version", "1.3.0")
    service_exception_report.set("xmlns", "http://www.opengis.net/ogc")

    # Service Exception
    service_exception = ET.SubElement(service_exception_report, "ServiceException")
    service_exception.set("code", exception_code)

    if locator:
        service_exception.set("locator", locator)

    service_exception.text = exception_text

    return prettify_xml(service_exception_report)
