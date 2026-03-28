import unittest

from utils import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node, extract_title
from leafnode import LeafNode
from textnode import TextNode, TextType
from parentnode import ParentNode

class TestTextToHTMLNode(unittest.TestCase):
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold")

    def test_italic(self):
        node = TextNode("This is italic", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic")

    def test_code(self):
        node = TextNode("This is code", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is code")

    def test_link(self):
        node = TextNode("This is link", TextType.LINK, "google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is link")
        self.assertTrue("href" in html_node.props)
        self.assertEqual(html_node.props["href"], "google.com")
    
    def test_image(self):
        node = TextNode("This is image", TextType.IMAGE, "google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertTrue("src" in html_node.props)
        self.assertTrue("alt" in html_node.props)
        self.assertEqual(html_node.props["src"], "google.com")
        self.assertEqual(html_node.props["alt"], "This is image")

class TestSplitNodes(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
                    TextNode("This is text with a ", TextType.TEXT),
                    TextNode("code block", TextType.CODE),
                    TextNode(" word", TextType.TEXT),
                ]
        self.assertEqual(new_nodes, expected)
    
    def test_bold(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
                    TextNode("This is text with a ", TextType.TEXT),
                    TextNode("bold", TextType.BOLD),
                    TextNode(" word", TextType.TEXT),
                ]
        self.assertEqual(new_nodes, expected)
    
    def test_italic(self):
        node = TextNode("This is text with a _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
                    TextNode("This is text with a ", TextType.TEXT),
                    TextNode("italic", TextType.ITALIC),
                    TextNode(" word", TextType.TEXT),
                ]
        self.assertEqual(new_nodes, expected)
    
    def test_all_code(self):
        node = TextNode("`This is one big code block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
                    TextNode("This is one big code block", TextType.CODE),
                ]
        self.assertEqual(new_nodes, expected)
    
    def test_all_bold(self):
        node = TextNode("**This is one big bold sentence**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
                    TextNode("This is one big bold sentence", TextType.BOLD),
                ]
        self.assertEqual(new_nodes, expected)
    
    def test_all_italic(self):
        node = TextNode("_This is one big italic sentence_", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
                    TextNode("This is one big italic sentence", TextType.ITALIC),
                ]
        self.assertEqual(new_nodes, expected)

    def test_multiple_bold(self):
        node = TextNode("This is text with **bold** word", TextType.TEXT)
        node2 = TextNode("This is text with **two** nice **bold** words", TextType.TEXT)
        node3 = TextNode("This is text with **three** **connecting ****bold** words", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node, node2, node3], "**", TextType.BOLD)
        expected = [
                    TextNode("This is text with ", TextType.TEXT),
                    TextNode("bold", TextType.BOLD),
                    TextNode(" word", TextType.TEXT),
                    TextNode("This is text with ", TextType.TEXT),
                    TextNode("two", TextType.BOLD),
                    TextNode(" nice ", TextType.TEXT),
                    TextNode("bold", TextType.BOLD),
                    TextNode(" words", TextType.TEXT),
                    TextNode("This is text with ", TextType.TEXT),
                    TextNode("three", TextType.BOLD),
                    TextNode(" ", TextType.TEXT),
                    TextNode("connecting ", TextType.BOLD),
                    TextNode("bold", TextType.BOLD),
                    TextNode(" words", TextType.TEXT),
                ]
        self.assertEqual(new_nodes, expected)
    
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_split_links(self):
        node = TextNode(
            "This is text with an [anchor](bootdet.com) and another [anchor2](youtube.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("anchor", TextType.LINK, "bootdet.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "anchor2", TextType.LINK, "youtube.com"
                ),
            ],
            new_nodes,
        )
    def test_split_images_simple(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )
    def test_split_links_simple(self):
        node = TextNode(
            "[anchor](bootdet.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("anchor", TextType.LINK, "bootdet.com"),
            ],
            new_nodes,
        )
    def test_split_images_empty(self):
        node = TextNode(
            "",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
            ],
            new_nodes,
        )
    def test_split_links_empty(self):
        node = TextNode(
            "",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
            ],
            new_nodes,
        )

    def test_text_to_text_nodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        textnodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            textnodes,
        )

class TestExtrackMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches)

    def test_extract_markdown_links_empty(self):
        matches = extract_markdown_links(
            "This is text with a link []() and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual([("", ""), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches)

    def test_extract_markdown_images_empty(self):
        matches = extract_markdown_images(
            "This is text with an ![]()"
        )
        self.assertListEqual([("", "")], matches)

class TestBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type_code(self):
        block = """
```
this is my code shalala
lol
```
"""
        block_type = block_to_block_type(block.strip())
        self.assertEqual(
            block_type,
            BlockType.CODE,
        )
    
    def test_block_to_block_type_heading(self):
        block = """
### This is my heading
and more heading?
"""
        block_type = block_to_block_type(block.strip())
        self.assertEqual(
            block_type,
            BlockType.HEADING,
        )

    def test_block_to_block_type_quote(self):
        block = """
>This is a quote
> This is a quote too
"""
        block_type = block_to_block_type(block.strip())
        self.assertEqual(
            block_type,
            BlockType.QUOTE,
        )

    def test_block_to_block_type_unordered_list(self):
        block = """
- first
- second
- third
"""
        block_type = block_to_block_type(block.strip())
        self.assertEqual(
            block_type,
            BlockType.UNORDERED_LIST,
        )
    def test_block_to_block_type_ordered(self):
        block = """
1. first
2. second
3. third
"""
        block_type = block_to_block_type(block.strip())
        self.assertEqual(
            block_type,
            BlockType.ORDERED_LIST,
        )

    def test_block_to_block_type_paragraph(self):
        block = """
1. first
2. second
4. Third
"""
        block_type = block_to_block_type(block.strip())
        self.assertEqual(
            block_type,
            BlockType.PARAGRAPH,
        )

class TestMarkdownToHTML(unittest.TestCase):
    def test_extract_title(self):
        md = "# Title  "
        self.assertEqual(extract_title(md), "Title")

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()

