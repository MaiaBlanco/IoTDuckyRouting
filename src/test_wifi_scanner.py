import iwlist
import pprint

points = iwlist.scan('wlp3s0')
cells = iwlist.parse(points)

pp = pprint.PrettyPrinter(indent=4)

pp.pprint(cells)
