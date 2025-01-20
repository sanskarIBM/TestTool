
def _generate_relative_xpath_id_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getXPath(element) {
            if (!element) return '';
            if (element.id) return `//*[@id="${element.id}"]`;

            const sameTagSiblings = Array.from(element.parentNode.children)
                .filter(e => e.tagName === element.tagName);

            const idx = sameTagSiblings.indexOf(element) + 1;

            return `${getXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
        }
        return getXPath(arguments[0]);
        """
        return element.parent.execute_script(script, element)
    except:
        return None

def _generate_relative_xpath_class_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getClassBasedXPath(element) {
    if (!element) return '';
    if (element.className) return `//*[@class="${element.className}"]`;

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getClassBasedXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getClassBasedXPath(arguments[0]);

        """
        return element.parent.execute_script(script, element)
    except:
        return None


def _generate_relative_xpath_name_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getNameBasedXPath(element) {
    if (!element) return '';
    if (element.getAttribute('name')) return `//*[@name="${element.getAttribute('name')}"]`;

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getNameBasedXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getNameBasedXPath(arguments[0]);


        """
        return element.parent.execute_script(script, element)
    except:
        return None


def _generate_relative_xpath_type_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getTypeBasedXPath(element) {
    if (!element) return '';
    if (element.getAttribute('type')) return `//*[@type="${element.getAttribute('type')}"]`;

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getTypeBasedXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getTypeBasedXPath(arguments[0]);


        """
        return element.parent.execute_script(script, element)
    except:
        return None


def _generate_relative_xpath_label_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getLabelBasedXPath(element) {
    if (!element) return '';
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) return `//label[@for="${element.id}"]`;

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getLabelBasedXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getLabelBasedXPath(arguments[0]);

        """
        return element.parent.execute_script(script, element)
    except:
        return None


def _generate_relative_xpath_combination_attributes_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getCombinedAttributesXPath(element) {
    if (!element) return '';

    const id = element.id ? `@id="${element.id}"` : '';
    const className = element.className ? `@class="${element.className}"` : '';
    const name = element.getAttribute('name') ? `@name="${element.getAttribute('name")}"` : '';
    const type = element.getAttribute('type') ? `@type="${element.getAttribute('type')}"` : '';

    const attributes = [id, className, name, type].filter(attr => attr).join(' and ');

    if (attributes) return `//*[${attributes}]`;

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getCombinedAttributesXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getCombinedAttributesXPath(arguments[0]);



        """
        return element.parent.execute_script(script, element)
    except:
        return None


def _generate_relative_xpath_text_based(self, element): # ID based Xpath Generation
    try:
        script = """function getTextBasedXPath(element) {
    if (!element) return '';
    if (element.textContent.trim()) return `//*[text()="${element.textContent.trim()}"]`;

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getTextBasedXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getTextBasedXPath(arguments[0]);
"""
        return element.parent.execute_script(script, element)
    except:
        return None

def _generate_relative_xpath_position_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getPositionalXPath(element) {
    if (!element) return '';

    const sameTagSiblings = Array.from(element.parentNode.children)
        .filter(e => e.tagName === element.tagName);

    const idx = sameTagSiblings.indexOf(element) + 1;

    return `${getPositionalXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getPositionalXPath(arguments[0]);

"""
        return element.parent.execute_script(script, element)
    except:
        return None

def _generate_relative_xpath_hierarchy_based(self, element): # ID based Xpath Generation
    try:
        script = """
        function getParentChildHierarchyXPath(element) {
    if (!element) return '';
    const parent = element.parentNode;

    const idx = Array.from(parent.children).indexOf(element) + 1;

    return `${getParentChildHierarchyXPath(parent)}/${element.tagName.toLowerCase()}[${idx}]`;
}
return getParentChildHierarchyXPath(arguments[0]);

"""
        return element.parent.execute_script(script, element)
    except:
        return None