#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame import item, exceptions, generic_response, widgets
from libqtopensesame import qtplugin
import openexp.canvas
import openexp.keyboard
import os.path
import shlex
from PyQt4 import QtGui, QtCore

class form_base(item.item, generic_response.generic_response):

	"""A text input display"""		
	
	def __init__(self, name, experiment, string=None):

		"""
		Constructor

		Arguments:
		name -- the name of the item
		experiment -- the experiment instance

		Keyword arguments:
		string -- a definition string
		"""

		self.item_type = "form_base"
		self.description = "A generic form plug-in"
		
		self.cols = '2;2'
		self.rows = '2;2'
		self.spacing = 10
		self.margins = '10;10;10;10'
		self._widgets = []		
		
		item.item.__init__(self, name, experiment, string)				
		
	def parse_line(self, line):
	
		"""
		Allows for arbitrary line parsing, for item-specific requirements

		Arguments:
		line -- a single definition line
		"""
		
		l = shlex.split(line.strip())
		if len(l) < 6 or l[0] != 'widget':
			return
			
		# Verify that the position variables are integers
		try:
			col = int(l[1])
			row = int(l[2])
			colspan = int(l[3])
			rowspan = int(l[4])
		except:
			raise exceptions.script_error( \
				_('Widget column and row should be numeric'))
			
		# Parse the widget into a dictionary and store it in the list of
		# widgets
		w = self.parse_keywords(line, unsanitize=True)				
		w['type'] = l[5]
		w['col'] = col
		w['row'] = row
		w['colspan'] = colspan
		w['rowspan'] = rowspan		
		self._widgets.append(w)						
			
	def to_string(self):
	
		"""
		Parse the widgets back into a definition string
		
		Returns:
		A definition string
		"""
	
		s = item.item.to_string(self, self.item_type)
		for w in self._widgets:
			w = w.copy()
			_type = w['type']
			col = w['col']
			row = w['row']
			colspan = w['colspan']
			rowspan = w['rowspan']			
			del w['type']
			del w['col']
			del w['row']
			del w['colspan']
			del w['rowspan']			
			s += '\twidget %s %s %s %s %s' % (col, row, colspan, rowspan, \
				_type)
			for keyword, value in w.items():
				s += ' %s="%s"' % (keyword, self.usanitize(value))
			s += '\n'
		s += '\n'
		return s
		
	def run(self):

		"""
		Run the item

		Returns:
		True on success, False on failure
		"""

		sri = self.time()
		self.set_item_onset(sri)
		resp = self._form._exec()
		rt = self.time() - sri
		
		self.experiment.set('response', self.usanitize(resp))
		self.experiment.set('response_%s' % self.name, self.usanitize(resp))
		self.experiment.set('response_time', rt)
		self.experiment.set('response_time_%s' % self.name, rt)				
		return True
		
	def prepare(self):
	
		"""Prepare for the run phase"""
		
		item.item.prepare(self)				
		
		# Prepare the form
		try:
			cols = [float(i) for i in self.cols.split(';')]
			rows = [float(i) for i in self.rows.split(';')]		
			margins = [float(i) for i in self.margins.split(';')]		
		except:
			raise exceptions.runtime_error( \
				_('cols, rows, and margins should be numeric values separated by a semi-colon'))									
		self._form = widgets.form(self.experiment, cols=cols, rows=rows, \
			margins=margins, spacing=self.spacing)		
		
		# Prepare the widgets
		for w in self._widgets:
			w = w.copy()
			_type = w['type']
			col = w['col']
			row = w['row']
			colspan = w['colspan']
			rowspan = w['rowspan']			
			del w['type']
			del w['col']
			del w['row']
			del w['colspan']
			del w['rowspan']	
			
			# Translate paths into full file names
			if 'path' in w:
				w['path'] = self.experiment.get_file(w['path'])
						
			# Create the widget and add it to the form
			_w = eval('widgets.%s(self._form, **w)' % _type)
			self._form.set_widget(_w, (col, row), colspan=colspan, \
					rowspan=rowspan)		
		return True

	def var_info(self):

		return generic_response.generic_response.var_info(self)

class qtform_base(form_base, qtplugin.qtplugin):

	"""GUI controls"""

	def __init__(self, name, experiment, string=None):

		"""
		Constructor

		Arguments:
		name -- the name of the item
		experiment -- the experiment instance

		Keyword arguments:
		string -- a definition string
		"""
		
		# Pass the word on to the parents
		form_base.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""Initialize the controls"""

		self.lock = True
		qtplugin.qtplugin.init_edit_widget(self, False)
		self.add_text('Edit the script to modify the form.')	
		self.add_stretch()	
		self.lock = False

	def apply_edit_changes(self):

		"""Apply the controls"""

		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return False
		return True

	def edit_widget(self):

		"""Update the controls"""

		self.lock = True
		qtplugin.qtplugin.edit_widget(self)
		self.lock = False
		return self._edit_widget
