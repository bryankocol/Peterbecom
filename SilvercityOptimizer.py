
SELECTORS = {
 'c_character': 'c_16',
 'c_comment': 'c_17',
 'c_commentdoc': 'c_18',
 'c_commentdockeyword': 'c_19',
 'c_commentdockeyworderror': 'c_20',
 'c_commentline': 'c_21',
 'c_commentlinedoc': 'c_22',
 'c_default': 'c_23',
 'c_identifier': 'c_24',
 'c_number': 'c_25',
 'c_operator': 'c_26',
 'c_preprocessor': 'c_27',
 'c_regex': 'c_28',
 'c_string': 'c_29',
 'c_stringeol': 'c_30',
 'c_uuid': 'c_31',
 'c_verbatim': 'c_32',
 'c_word': 'c_33',
 'c_word2': 'c_34',
 'code_default': 'c_0',
 'css_class': 'c_1',
 'css_comment': 'c_2',
 'css_default': 'c_3',
 'css_directive': 'c_4',
 'css_doublestring': 'c_5',
 'css_id': 'c_6',
 'css_identifier': 'c_7',
 'css_important': 'c_8',
 'css_operator': 'c_9',
 'css_pseudoclass': 'c_10',
 'css_singlestring': 'c_11',
 'css_tag': 'c_12',
 'css_unknown_identifier': 'c_13',
 'css_unknown_pseudoclass': 'c_14',
 'css_value': 'c_15',
 'h_asp': 'h_0',
 'h_aspat': 'h_1',
 'h_attribute': 'h_2',
 'h_attributeunknown': 'h_3',
 'h_cdata': 'h_4',
 'h_comment': 'h_5',
 'h_default': 'h_6',
 'h_doublestring': 'h_7',
 'h_entity': 'h_8',
 'h_number': 'h_9',
 'h_other': 'h_10',
 'h_script': 'h_11',
 'h_singlestring': 'h_12',
 'h_tag': 'h_13',
 'h_tagend': 'h_14',
 'h_tagunknown': 'h_15',
 'h_xmlend': 'h_16',
 'h_xmlstart': 'h_17',
 'p_character': 'p_30',
 'p_classname': 'p_31',
 'p_commentblock': 'p_32',
 'p_commentline': 'p_33',
 'p_default': 'p_34',
 'p_defname': 'p_35',
 'p_identifier': 'p_36',
 'p_number': 'p_37',
 'p_operator': 'p_38',
 'p_string': 'p_39',
 'p_stringeol': 'p_40',
 'p_triple': 'p_41',
 'p_tripledouble': 'p_42',
 'p_word': 'p_43',
 'pl_array': 'p_0',
 'pl_backticks': 'p_1',
 'pl_character': 'p_2',
 'pl_commentline': 'p_3',
 'pl_datasection': 'p_4',
 'pl_default': 'p_5',
 'pl_error': 'p_6',
 'pl_hash': 'p_7',
 'pl_here_delim': 'p_8',
 'pl_here_q': 'p_9',
 'pl_here_qq': 'p_10',
 'pl_here_qx': 'p_11',
 'pl_identifier': 'p_12',
 'pl_longquote': 'p_13',
 'pl_number': 'p_14',
 'pl_operator': 'p_15',
 'pl_pod': 'p_16',
 'pl_preprocessor': 'p_17',
 'pl_punctuation': 'p_18',
 'pl_regex': 'p_19',
 'pl_regsubst': 'p_20',
 'pl_scalar': 'p_21',
 'pl_string': 'p_22',
 'pl_string_q': 'p_23',
 'pl_string_qq': 'p_24',
 'pl_string_qr': 'p_25',
 'pl_string_qw': 'p_26',
 'pl_string_qx': 'p_27',
 'pl_symboltable': 'p_28',
 'pl_word': 'p_29',
 'yaml_comment': 'y_0',
 'yaml_default': 'y_1',
 'yaml_document': 'y_2',
 'yaml_identifier': 'y_3',
 'yaml_keyword': 'y_4',
 'yaml_number': 'y_5',
 'yaml_reference': 'y_6'}

import re
def GenerateSelectorsDict(css):
    """ This function creates a dictionary that maps the
    old and long name to an optimized one. Use this function to
    generate a new variable value for the SELECTORS variable above.
    >>> from pprint import pprint
    >>> pprint (_GenerateSelectorsDict(css))
    The copy the output and change this file.
    """

    selector_regex = re.compile(r'\.(\w+)\s+{', re.I)
    counters = {}
    selectors = {}
    for each in selector_regex.findall(css):
        firstletter = each.split('_')[0].lower()
        count = counters.get(firstletter,0)
        new = '%s_%s'%(firstletter, count)
        selectors[each] = new
        counters[firstletter] = count+1

    return selectors

def GenerateNewSilverCityCSSFile(css):
    selector_regex = re.compile(r'(\.(\w+)(\s+){)', re.I)
    for whole, part, extraspace in selector_regex.findall(css):
        css = css.replace(whole, '.%s%s{'%(SELECTORS[part], extraspace))

    css_comments = re.compile(r'/\*.*?\*/', re.MULTILINE|re.DOTALL)
    css = css_comments.sub('', css) # remove comments
    css = re.sub(r'\s\s+', '', css) # >= 2 whitespace becomes no whitespace
    css = re.sub(r'\s+{','{', css) # no whitespace until start of selector
    css = re.sub(r'\s}','}', css) # no whitespace until end of selector
    css = re.sub(r';}', r';}\n', css) # ok to have a linebreak here
    css = re.sub(r'{\s\s+', '{', css) # whatspace after {
    css = re.sub(r':\s+',':', css) # no whitespace after colon
    css = re.sub(r',\s',r',', css) # no extraspace between commas
    css = re.sub(r'}.',r'}\n.', css)
    return css.strip()


def OptimizeSilverCityHTMLOutput(html, xhtml=True):
    
    # 1. Remove all "<x>_default" tags
    done_space_tags = []
    space_tag = re.compile(r'(<span class="\w+_default">(.*?)</span>)',
                           re.I|re.MULTILINE|re.DOTALL)
    for tag, spaces in space_tag.findall(html):
        if tag not in done_space_tags:
            html = html.replace(tag, spaces)
            done_space_tags.append(tag)
            
    # 2. Use shorter names of the selectors
    done_originals = []
    for orig, new in SELECTORS.items():
        neworig = 'class="%s"'%orig
        if neworig not in done_originals:
            if xhtml:
                new = 'class="%s"'%new
            else:
                new = 'class=%s'%new
            done_originals.append(neworig)
            html = html.replace(neworig, new)
        
    return html

if __name__=='__main__':
    # return the content for an optimized default.css file
    import os
    path = 'dtml'
    old = 'silvercity.css.dtml'
    filepath = os.path.join(path, old)
    css = open(filepath).read()
    print GenerateNewSilverCityCSSFile(css)
    
    





