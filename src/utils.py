from leafnode import LeafNode
from textnode import TextNode, TextType
import re
from enum import Enum
from parentnode import ParentNode

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text.strip())
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text.strip())
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text.strip())
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text.strip())
        case TextType.LINK:
            return LeafNode(tag="a", value=text_node.text.strip(), props={"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode(tag="img", value="", props={"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("Invalid text type")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
    
        parts = old_node.text.split(delimiter)
        if len(parts) == 1:
            new_nodes.append(old_node)
            continue
        if len(parts) % 2 == 0:
            raise Exception("Invalid Markdown syntax")
        for i in range(len(parts)):
            if i % 2 == 0:
                if parts[i] != "":
                    new_nodes.append(TextNode(text=parts[i], text_type=TextType.TEXT))
            else:
                new_nodes.append(TextNode(text=parts[i], text_type=text_type))
    return new_nodes
        
def extract_markdown_images(text):
    return re.findall(r"\!\[(.*?)\]\((.*?)\)", text)

def extract_markdown_links(text):
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        images = extract_markdown_images(old_node.text)
        remainder = old_node.text
        for image in images:
            delimiter = f"![{image[0]}]({image[1]})"
            text1 = remainder.split(delimiter)[0]
            remainder = delimiter.join(remainder.split(delimiter)[1:])
            if text1 != "":
                new_nodes.append(TextNode(text1, TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
        if remainder != "":
            new_nodes.append(TextNode(remainder, TextType.TEXT))
    return new_nodes
            
def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        links = extract_markdown_links(old_node.text)
        remainder = old_node.text
        for link in links:
            delimiter = f"[{link[0]}]({link[1]})"
            text1 = remainder.split(delimiter)[0]
            remainder = delimiter.join(remainder.split(delimiter)[1:])
            if text1 != "":
                new_nodes.append(TextNode(text1, TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
        if remainder != "":
            new_nodes.append(TextNode(remainder, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text.replace("\n", " "), TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    return split_nodes_link(nodes)

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks_to_return = []
    for block in blocks:
        block = block.strip()
        if block != "":
            blocks_to_return.append(block)
    return blocks_to_return

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered list"

def block_to_block_type(block):
    #Heading
    if block.startswith("# ") or block.startswith("## ") or block.startswith("### ") or block.startswith("#### ") or block.startswith("##### ") or block.startswith("###### "):
        return BlockType.HEADING
    #Code
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    #Quote
    confirmed = True
    for line in block.split("\n"):
        if not line.startswith(">"):
            confirmed = False
            break
    if confirmed:
        return BlockType.QUOTE
    #Unordered list
    confirmed = True
    for line in block.split("\n"):
        if not line.startswith("- "):
            confirmed = False
            break
    if confirmed:
        return BlockType.UNORDERED_LIST
    #Ordered list
    confirmed = True
    index = 1
    for line in block.split("\n"):
        if not line.startswith(f"{index}. "):
            confirmed = False
            break
        index += 1
    if confirmed:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        type = block_to_block_type(block)
        match type:
            case BlockType.PARAGRAPH:
                children.append(ParentNode("p", [text_node_to_html_node(text_node) for text_node in text_to_textnodes(block)]))
            case BlockType.CODE:
                children.append(ParentNode("pre", [text_node_to_html_node(TextNode(clear_markdowns(block, type), TextType.CODE))]))
            case BlockType.QUOTE:
                children.append(ParentNode("blockquote", [text_node_to_html_node(text_node) for text_node in text_to_textnodes(clear_markdowns(block, type))]))
            case BlockType.UNORDERED_LIST:
                children.append(ParentNode("ul", [ParentNode("li", [text_node_to_html_node(text_node) for text_node in text_to_textnodes("- ".join(child.split("- ")[1:]))]) for child in block.split("\n")]))
            case BlockType.ORDERED_LIST:
                children.append(ParentNode("ol", [ParentNode("li", [text_node_to_html_node(text_node) for text_node in text_to_textnodes(".".join(child.split(".")[1:]))]) for child in block.split("\n")]))
            case BlockType.HEADING:
                count = 0
                while block[count] == "#":
                    count += 1
                children.append(ParentNode(f"h{count}", [text_node_to_html_node(text_node) for text_node in text_to_textnodes(clear_markdowns(block, type))]))
    return ParentNode("div", children)

def clear_markdowns(block, block_type):
    match block_type:
        case BlockType.CODE:
            return "\n".join("```\n".join(block.split("```\n")[1:]).split("```")[:-1])
        case BlockType.QUOTE:
            quotes = []
            for quote in block.split("\n"):
                if quote.startswith("> "):
                    quotes.append("> ".join(quote.split("> ")[1:]))
                else:
                    quotes.append(">".join(quote.split(">")[1:]))
            return "\n".join(quotes)
        case BlockType.HEADING:
            count = 0
            while block[count] == "#":
                count += 1
            return block[count+1:]
        case _:
            return block

def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("Error: no header found")