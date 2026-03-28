import unittest

from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode("<p>", "This is a node", [], {"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_htmlnode_tag(self):
        node = HTMLNode("<p>")
        node2 = HTMLNode("<p>")
        self.assertEqual(node.tag, node2.tag)

    def test_htmlnode_value(self):
        node = HTMLNode(value="This is a node")
        node2 = HTMLNode(value="This is a node")
        self.assertEqual(node.value, node2.value)


if __name__ == "__main__":
    unittest.main()
