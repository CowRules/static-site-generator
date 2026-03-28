from htmlnode import HTMLNode

class ParentNode(HTMLNode):

    def __init__(self, tag, children, props={}):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError()
        if self.children is None:
            raise ValueError("No children provided")
        result = ""
        for child in self.children:
            result += child.to_html()
        return f"<{self.tag}>{result}</{self.tag}>"
