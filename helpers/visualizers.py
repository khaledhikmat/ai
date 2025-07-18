import pyvis 

# this uses pyvis to visualize the graph
def visualize_graph(query_graph, node_attrs, output="network.html"):
    visual_graph = pyvis.network.Network()
    node_labels = node_attrs.get("labels", {})
    node_colors = node_attrs.get("colors", {})
    node_shapes = node_attrs.get("shapes", {})
    node_images = node_attrs.get("images", {})
    node_icons = node_attrs.get("icons", {})

    for node in query_graph.nodes:
        node_label = list(node.labels)[0]
        node_text = node[node_labels[node_label]]
        color = node_colors.get(node_label, "#cccccc")
        shape = node_shapes.get(node_label, "circle")
        if shape == "circle":
            # this shows the label outside the circle
            visual_graph.add_node(node.element_id, node_text, color=color)
            # this shows the label inside the circle
            # visual_graph.add_node(node.element_id, node_text, shape=shape, color=color)
        elif shape == "image":
            image = node_images.get(node_label, None)
            if image:
                visual_graph.add_node(node.element_id, node_text, shape=shape, image=image, color=color)
            else:
                visual_graph.add_node(node.element_id, node_text, shape=shape, color=color)
        elif shape == "icon":
            icon = node_icons.get(node_label, None)
            if icon:
                visual_graph.add_node(node.element_id, node_text, shape=shape, icon=icon, color=color)
            else:
                visual_graph.add_node(node.element_id, node_text, shape=shape, color=color)
        else:
            # Default to circle shape if not specified
            visual_graph.add_node(node.element_id, node_text, shape=shape, color=color)
 
    for relationship in query_graph.relationships:
        visual_graph.add_edge(
            relationship.start_node.element_id,
            relationship.end_node.element_id,
            # I commented out the labels because the graph gets congested with labels
            # The relationship type is avilable as tooltip on hover 
            #label=relationship.type,
            title=relationship.type
        )

    visual_graph.show(output, notebook=False)

