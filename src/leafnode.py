from htmlnode import HTMLNode

class LeafNode(HTMLNode):

    def __init__(self, tag, value, props={}):
        super().__init__(tag, value, props=props)

    def to_html(self):
        if self.value == None:
            raise ValueError()
        if self.tag == None:
            return self.value
        else:
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"tag: {self.tag}\nvalue: {self.value}\n props: {self.props}"
