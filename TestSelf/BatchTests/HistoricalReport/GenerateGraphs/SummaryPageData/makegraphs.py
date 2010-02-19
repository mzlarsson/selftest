#!/usr/bin/env python

import pylab

pylab.clf()
figure4 = pylab.figure(1)
figure4.set_figwidth(9.4488188976377945)
figure4.set_figheight(7.8740157480314963)
axessubplot4 = pylab.subplot(111)
text4 = pylab.title("Test results for Application: 'Application One'  Version: 'version2'", fontsize=10, family='monospace')
axessubplot4.set_autoscale_on(False)
l1, = axessubplot4.plot([0, 1, 2, 3, 4, 5], [2, 2, 2, 8, 8, 15], color='#CEEFBD', linewidth=2, linestyle='-', label='Succeeded tests')
l1.set_visible(False)
l2, = axessubplot4.plot([1, 2, 3], [2, 4, 8], color='#FF3118', linewidth=2, linestyle='-', label='Failed tests')
l2.set_visible(False)
l3, = axessubplot4.plot([4, 5], [8, 18], color='#FF3118', linewidth=2, linestyle='-', label='Failed tests')
l3.set_visible(False)
axessubplot4.set_autoscale_on(True)
axessubplot4.fill_between([0, 1, 2, 3, 4, 5], [0, 0, 0, 0, 0, 0], [2, 2, 2, 8, 8, 15], color='#CEEFBD', linewidth=2, linestyle='-')
where = [False, True, True, True, False, True]
axessubplot4.fill_between([0, 1, 2, 3, 4, 5], [2, 2, 2, 8, 8, 15], [2, 2, 4, 8, 8, 18], where=where, color='#FF3118', linewidth=2, linestyle='-')
#axessubplot4.fill_between([4, 5], [8, 15], [8, 18], color='#FF3118', linewidth=2, linestyle='-')
pylab.xticks([0, 1, 2, 3, 4, 5], ['14Jan2006', '15Jan2006', '16Jan2006', '17Jan2006', '18Jan2006', '19Jan2006'])
silent_list8 = axessubplot4.get_xticklabels()
pylab.setp(silent_list8, 'rotation', 90, fontsize=7)
p = pylab.Rectangle((0, 0), 1, 1, fc="#FF3118")
p2 = pylab.Rectangle((0, 0), 1, 1, fc="#CEEFBD")
legend4 = axessubplot4.legend([ p, p2 ], ('Failed tests', 'Succeeded tests'), 'best', shadow=False)
fancybboxpatch4 = legend4.get_frame()
fancybboxpatch4.set_alpha(0.5)
figure4.subplots_adjust(bottom=0.25)
figure4.savefig('results.app1.version2.png', dpi=100)