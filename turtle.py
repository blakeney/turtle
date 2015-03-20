#!/usr/bin/env python

import subprocess
import sys
import urwid as ur
import yaml
from ui.widgets import *

I_TITLEBAR = 0
I_BODY = 1
I_PREVIEW = 2
I_BUTTONS = 3
I_OUTPUT = 4

def command_form_from_file(filename):
	f = open(filename)
	raw = yaml.safe_load(f)
	f.close()
	command = raw['command']
	params = raw['params']
	form = CommandForm(raw['title'], command, params)
	return form

class CommandForm:
	def __init__(self, title, command, params=[], env={}, user=''):
		self.title = title
		self.command = command
		self.params = params
		self.env = env
		self.user = user
	
	def __len__(self):
		return len(self.params)

	def __str__(self):
		return self.command + ' ' +  ' '.join(['%s %s' % (v['flag'], v['value']) for v in self.params if v.has_key('value')])
	
	def set_values(self, pile):
		i = 0
		while i < len(self):
			v = pile[i].get_value()
			if v != None:
				self.params[i]['value'] = v
			elif self.params[i].has_key('value'):
				del(self.params[i]['value'])
			i += 1

class FormListBox(ur.ListBox):
	def __init__(self, form, separator=': '):
		self.form = form
		self.separator = separator
		self.widget_factory = WidgetFactory(separator)
		body = ur.SimpleFocusListWalker([
			ur.AttrWrap(ur.Text(form.title), 'command'),
			ur.Pile(self._get_widgets()),
			ur.AttrWrap(ur.Text(''), 'command'),
			ur.Columns([
				ur.AttrWrap(ur.Button('Execute', self.execute), 'execute'),
				ur.AttrWrap(ur.Button('Reset', self.reset), 'reset'),
				ur.AttrWrap(ur.Button('Exit', self.exit), 'exit')
				]),
			ur.AttrWrap(ur.Text(''), 'output')
			])
		super(FormListBox, self).__init__(body)
		self.update()

	def _get_widgets(self):
		return [self.widget_factory.get_widget(param) for param in self.form.params]

	def exit(self, *args):
		self.update()
		raise ur.ExitMainLoop()
	
	def execute(self, button):
		self.update()
		proc = subprocess.Popen(str(self.form), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# TODO: Update output periodically to make more useful for long-running processes
		output = proc.communicate()
		self.body[I_OUTPUT].set_text(output[1] + output[0])

	def reset(self, button):
		[self.body[I_BODY][i].reset() for i in range(0, len(self.form))]
		self.body[I_OUTPUT].set_text('')
		self.update()

	def update(self):
		self.form.set_values(self.body[I_BODY])
		self.body[I_PREVIEW].set_text(str(self.form))

	def keypress(self, size, key):
		key = super(FormListBox, self).keypress(size, key)
		if key == 'ctrl n' or key == 'down':
			self.focus_position = self.move(1)
		elif key == 'ctrl p' or key == 'up':
			self.focus_position = self.move(-1)
		elif key == 'ctrl d':
			self.exit()
		else:
			return key
	
	def move(self, delta):
		self.update()
		if self.focus_position == I_BODY:
			return self._move_helper(self.focus_position, delta, len(self.form), I_BODY, I_BUTTONS)
		elif self.focus_position == I_BUTTONS:
			return self._move_helper(self.focus_position, delta, 3, I_BODY, I_BUTTONS)
		else:
			return self.focus_position
	
	def _move_helper(self, major_index, delta, max_minor_index, prev_major_index, next_major_index):
		minor_index = self.body[major_index].focus_position
		if minor_index + delta < 0:
			self.body[major_index].focus_position = 0
			return prev_major_index
		elif minor_index + delta >= max_minor_index:
			self.body[major_index].focus_position = max_minor_index - 1
			return next_major_index
		else:
			self.body[major_index].focus_position = minor_index + delta
			return major_index

def __main__():
	if len(sys.argv) != 2:
		raise ValueError("Exactly one command configuration file must be specified")
	filename = sys.argv[1]
	form = command_form_from_file(filename)
	palette = [
			('command', 'black,bold', 'yellow'),
			('output', 'black,bold', 'dark green'),
			('execute', 'white,bold', 'dark red'),
			('exit', 'white,bold', 'black'),
			('reset', 'white,bold', 'dark blue')
			]
	ur.MainLoop(FormListBox(form), palette).run()
	print form

if __name__ == '__main__':
	__main__()

