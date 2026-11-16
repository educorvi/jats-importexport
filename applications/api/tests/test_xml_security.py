import io

import pytest
from api.services.upload import _create_xml_parser
from lxml import etree


@pytest.mark.parametrize('kind', ['entity', 'dtd', 'parameter'])
def test_external_local_resources_are_rejected(tmp_path, kind):
    secret = tmp_path / 'private.txt'
    secret.write_text('AUDIT_SECRET_MARKER')
    uri = secret.as_uri()
    declarations = {
        'entity': f'<!DOCTYPE article [<!ENTITY secret SYSTEM "{uri}">]><article>&secret;</article>',
        'dtd': f'<!DOCTYPE article SYSTEM "{uri}"><article/>',
        'parameter': f'<!DOCTYPE article [<!ENTITY % secret SYSTEM "{uri}">%secret;]><article/>',
    }
    with pytest.raises(etree.XMLSyntaxError, match='not allowed'):
        etree.parse(io.BytesIO(declarations[kind].encode()), _create_xml_parser())


def test_unknown_remote_dtd_is_rejected():
    xml = b'<!DOCTYPE article SYSTEM "https://example.invalid/unknown.dtd"><article/>'
    with pytest.raises(etree.XMLSyntaxError, match='not allowed'):
        etree.fromstring(xml, _create_xml_parser())


def test_bundled_jats_dtd_and_entities_still_work():
    xml = b'<!DOCTYPE article SYSTEM "JATS-journalpublishing1.dtd"><article><p>&alpha;</p></article>'
    root = etree.fromstring(xml, _create_xml_parser())
    assert root.find('p').text == '\u03b1'


def test_plain_xml_file_stream_still_works(tmp_path):
    source = tmp_path / 'article.xml'
    source.write_text('<article><p>Content</p></article>')
    with source.open('rb') as stream:
        tree = etree.parse(stream, _create_xml_parser())
    assert tree.find('p').text == 'Content'
