"""CLI for testing the PloneStorageAdapter against a live Plone instance."""

import argparse
import sys


def cmd_upload_file(args):
    """Execute the upload-file subcommand to post a local binary to Plone."""
    from .PloneStorageAdapter import PloneStorageAdapter

    adapter = PloneStorageAdapter()
    with open(args.file, "rb") as f:
        url = adapter.upload_file(f, args.container)
    print(f"Uploaded to: {url}")


def cmd_save_document(args):
    """Execute the save-document subcommand to serialize a local JATS XML to Plone."""
    from jats_classes import JATSDocument

    from .PloneStorageAdapter import PloneStorageAdapter

    with open(args.xml, encoding="utf-8") as f:
        xml_content = f.read()

    document = JATSDocument.from_xml(xml_content, args.xsd)
    adapter = PloneStorageAdapter()
    url = adapter.save_jats_document(document, args.container)
    print(f"Saved to: {url}")


def cmd_get_document(args):
    """Execute the get-document subcommand to fetch article structure from Plone."""
    from .PloneStorageAdapter import PloneStorageAdapter

    adapter = PloneStorageAdapter()
    document = adapter.get_jats_document(args.path)
    print(document)


def main():
    """Configure argparse and dispatch to CLI subcommand execution functions."""
    parser = argparse.ArgumentParser(
        prog="jats-plone",
        description="Test the PloneStorageAdapter against a Plone instance.\n\n"
        "Required environment variables:\n"
        "  PLONE_BASE_URL   Base URL of the Plone instance\n"
        "  PLONE_USERNAME   Plone username\n"
        "  PLONE_PASSWORD   Plone password",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # upload-file
    upload_parser = subparsers.add_parser("upload-file", help="Upload a file to Plone")
    upload_parser.add_argument("file", help="Path to the local file to upload")
    upload_parser.add_argument(
        "--container",
        default="",
        help="Target container path in Plone (e.g. 'vol1/issue2'). Defaults to the Plone root.",
    )

    # save-document
    save_parser = subparsers.add_parser(
        "save-document", help="Parse a JATS XML file and save it to Plone"
    )
    save_parser.add_argument("xml", help="Path to the JATS XML file")
    save_parser.add_argument(
        "container",
        help="Target container path in Plone (e.g. 'vol1/issue2')",
    )
    save_parser.add_argument(
        "--xsd",
        default=None,
        help="Path to XSD schema for validation",
    )

    # get-document
    get_parser = subparsers.add_parser(
        "get-document",
        help="Retrieve a JATS document from Plone",
    )
    get_parser.add_argument("path", help="Path of the document in Plone")

    args = parser.parse_args()

    try:
        if args.command == "upload-file":
            cmd_upload_file(args)
        elif args.command == "save-document":
            cmd_save_document(args)
        elif args.command == "get-document":
            cmd_get_document(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
