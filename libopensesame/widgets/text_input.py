#-*- coding:utf-8 -*-

"""
This file is part of openexp.

openexp is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

openexp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with openexp.  If not, see <http://www.gnu.org/licenses/>.
"""

from label import label
from openexp.keyboard import keyboard

class text_input(label):

	"""A multiline text input widget"""

	def __init__(self, form, text='', frame=True, center=False, stub='Type here ...', return_accepts=False, var=None):
	
		"""<DOC>
		Constructor
		
		Arguments:
		form -- the parent form		
		
		Keyword arguments:
		text -- the text to start with (default='')
		frame -- indicates whether a frame should be drawn around the widget
				 (default=False)
		center -- indicates whether the text should be centered (default=False)
		stub -- a text string that should be shown whenever the user has not
				entered any text (default='Type here ...')
		var -- the name of the experimental variable that should be used to log
			   the widget status (default=None)					
		</DOC>"""
		
		if type(return_accepts) != bool:
			return_accepts = return_accepts == 'yes'								
	
		label.__init__(self, form, text, frame=frame, center=center)
		self.type = 'text_input'		
		self.stub = stub
		self.prompt = '_'
		self.return_accepts = return_accepts
		self.var = var
		self.text = text
		self.set_var(text)
		
	def render(self):
	
		"""<DOC>
		Draws the widget
		</DOC>"""	

		if self.frame:
			if self.focus:
				self.draw_frame(self.rect, style='active')
			else:
				self.draw_frame(self.rect, style='light')
		if self.text == '' and not self.focus:
			self.draw_text(self.stub, html=False)	
		elif self.focus:
			self.draw_text(self.text+self.prompt, html=False)	
		else:
			self.draw_text(self.text, html=False)	
				
	def on_mouse_click(self, pos):
	
		"""<DOC>
		Is called whenever the user clicks on the widget. Activates the text
		input for typing text.
		
		Arguments:
		pos -- an (x, y) tuple		
		</DOC>"""	
		
		self.focus = True
		my_keyboard = keyboard(self.form.experiment)
		while True:		
			self.form.render()		
			resp, time = my_keyboard.get_key()
			try:
				o = ord(resp)
			except:
				o = None
			if resp == 'space':			
				self.text += ' '
			elif resp == 'backspace' or o == 8:
				self.text = self.text[:-1]
			elif resp == 'tab':
				self.focus = False
				return None
			elif resp == 'return':
				if self.return_accepts:
					return self.text
				else:
					self.focus = False
					return None
			elif len(resp) == 1:
				self.text += resp
			self.set_var(self.text)
						
