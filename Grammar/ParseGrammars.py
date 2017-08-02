from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from re import sub


class LayerConstraint():
    """Object used to define areas based on certain constraints. For example,
    land within 1 tile of water (i.e. coasts) or elevation above 200"""
    def __init__(self, name, constraints):
        self.name = name
        self.constraints = constraints
        self.resultantArray = np.where(map1['elevation']>200,0,1)

    def __str__(self):
        return 'Layer Constraint defined by:{}'.format(self.constraints)

    def render(self, loc='C:\\Users\\Brendan\\Documents\\World Builder\\'):
        x, y = self.resultantArray.shape
        if len(np.unique(resultantArray)) == 2:
            o = Image.new('1', (x, y))
        else:
            o = Image.new('L', (x, y))
        px = o.load()
        for lx in range(x):
            for ly in range(y):
                px[lx, ly] = int(self.resultantArray[lx, ly])
        o.save('{}{}.png'.format(loc,self.name))

    def parse(self):
        pass


def readGrammar(fn):
    f = open(fn, 'r')
    for line in f.readlines():
        pass


indentLexer = Grammar("""
text= line+
line = indent ~".*" "\\n"
indent=SOL tab*
tab = "\t"
SOL = ~"^"m
""")




mygrammar = Grammar("""

simple="{" numbers ">test}\\n"
statement= expression nl?
expression = function / selection / object
selection="{" (opexpression)? text (opexpression)? "}"
function ="(" text (sep parameters)? ")"
object="[" text (sep parameters)? "]"
nl = "\\n"
sep= ":"

opexpression= (operator numbers) / (numbers operator)
operator= ~"[<>]"
parameters= text ("," (numbers/text) )*
text= ~"[A-Z]+"i numbers?
numbers= ~"[0-9]+"
""")


class indentVisitor(NodeVisitor):
    def __init__(self,grammar):
        self.grammar=grammar
        self.indentLevel =-1
        self.openBlocks=[]
        self.blocks=[]

    def generic_visit(self, node, b):
        pass

    def visit_indent(self, node, children):
        # doesn't recognize spaces as indentation markers
        newLevel = node.text.count('\t')
        self.token = newLevel-self.indentLevel
        self.indentLevel = newLevel

    def visit_line(self,node,c):
        if self.token > 0:
            for _ in range(abs(self.token)):
                self.openBlocks.append((self.indentLevel,node.start))
        elif self.token < 0:
            for _ in range(abs(self.token)):
                blockstarted = self.openBlocks.pop()
                self.blocks.append((blockstarted[0], blockstarted[1], node.start))
        else:
            pass


def getIndentTree():
    dic = {}
    t = file(r'C:\Users\Brendan\Documents\World Builder\myProgram.txt', 'r')
    y = indentVisitor(indentLexer)
    text = t.read()
    tlines = text.split('\n')
    y.parse(text)
    while len(y.openBlocks) != 0:
        i, s = y.openBlocks.pop()
        y.blocks.append((i, s, len(text)))

    indices = []
    for i in sorted(y.blocks):
        s, e = i[1:]
        start = text[0:s].count('\n')+1
        length = text[s:e].count('\n')-1
        indices.append((i[0], start, start+length))

    roots = filter(lambda x: x[0]==0, indices)
    for r in roots:
        indices.remove(r)
    for r in roots:
        directChildren = filter(lambda x: x[0]==1 and x[1] >=r[1] and x[2]<=r[2], indices)
        if len(directChildren)==0:
            dic[r[1:]]=None
        for child in directChildren:
            dic[r[1:]]=[x[1:] for x in directChildren]
            indices = map(lambda x: (x[0]-1, x[1], x[2]),indices)#directChildren are new roots
            getChildren(indices,text,dic)
    return dic
class funcRunner(NodeVisitor):
    """docstring for funcRunner."""
    def __init__(self, grammar):
        self.grammar = grammar


    def getProperties(self, node, name,ps=[]):
        if len(node.children)== 0:
            return None
        for c in node.children:
            if c.expr_name==name:
                ps.append(c.text)
            if self.getProperties(c,name) not in  [None,' ',[]]:
                ps.append(self.getProperties(c,name))
        return ps

    def generic_visit(self, a, b):
        pass

    def visit_function(self, node, children):
        pass

    def visit_simple(self,node,c):
        print (c)

    def visit_opexpression(self, node, children):
        print (children)


x = funcRunner(mygrammar)
t = open(r'C:\Users\Brendan\Documents\World Builder\myProgram.txt','r').read()
x.parse(t)
