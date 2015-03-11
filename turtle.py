#!/usr/bin/env python

import subprocess
import sys
import urwid as ur
import yaml

def command_form_from_file(filename):
	f = open(filename)
	raw = yaml.safe_load(f)
	f.close()
	command = raw['command']
	params = raw['params']
	form = CommandForm(command, params)
	return form

class CommandForm:
	def __init__(self, command, params=[], env={}, user='', separator=': '):
		self.command = command
		self.params = params
		self.env = env
		self.user = user
		self.separator = separator
	
	def __len__(self):
		return len(self.params)

	def __str__(self):
		return self.command + ' ' +  ' '.join(['%s %s' % (v['flag'], v['value']) for v in self.params if v.has_key('value')])
	
	def get_widgets(self):
		return [self._get_widget(param) for param in self.params]

	def _get_widget(self, param):
		wtype = param['type']
		if wtype == 'string':
			return ur.Edit('%s%s' % (param['label'], self.separator), '')
		elif wtype == 'boolean':
			return ur.CheckBox(param['label'], param['default'])
		elif wtype == 'select':
			return SelectPile(param['label'], param['options'])
		else:
			raise ValueError("Unrecognized parameter type %s" % wtype)

	def set_values(self, pile):
		i = 0
		while i < len(self):
			v = self.extract_value(pile[i], i)
			if v != None:
				self.params[i]['value'] = v
			elif self.params[i].has_key('value'):
				del(self.params[i]['value'])
			i += 1

	def reset_widgets(self, pile):
		i = 0
		while i < len(self):
			wtype = self.params[i]['type']
			if wtype == 'string':
				pile[i].set_edit_text('')
			elif wtype == 'boolean':
				pile[i].set_state(self.params[i]['default'])
			elif wtype == 'select':
				pile[i].reset()
			else:
				raise ValueError("Unrecognized parameter type %s" % wtype)
			i += 1

	def extract_value(self, widget, index):
		wtype = self.params[index]['type']
		if wtype == 'string':
			return widget.get_edit_text()
		elif wtype == 'boolean':
			if widget.get_state():
				return '' 
			else:
				return None
		elif wtype == 'select':
			return widget.get_selection()
		else:
			raise ValueError("Unrecognized parameter type %s" % wtype)

class FormListBox(ur.ListBox):
	def __init__(self, form):
		self.form = form
		body = ur.SimpleFocusListWalker([
			ur.Pile(form.get_widgets()),
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

	def exit(self, *args):
		self.update()
		raise ur.ExitMainLoop()
	
	def execute(self, button):
		self.update()
		output = subprocess.Popen(str(self.form), shell=True, stdout=subprocess.PIPE).stdout.read()
		self.body[3].set_text(output)

	def reset(self, button):
		self.form.reset_widgets(self.body[0])
		self.body[3].set_text('')
		self.update()

	def update(self):
		#vals = [self.body[0][i].edit_text for i in range(0, len(self.form))]
		self.form.set_values(self.body[0])
		self.body[1].set_text(str(self.form))

	def keypress(self, size, key):
		key = super(FormListBox, self).keypress(size, key)
		if self.focus_position == 0:
			if key == 'enter':
				self.update()
				if self.focus.focus_position < len(self.form) - 1:
					self.focus.focus_position += 1
				else:
					self.focus_position += 2
			elif key == 'ctrl d':
				self.exit()
			else:
				return key
		else: # TODO: Handle ctrl d outside of form
			return key

class SelectPile(ur.Pile):
	def __init__(self, label, option_list, focus_item=None):
		self.length = len(option_list)
		self.selection = None
		self.group = []
		widget_list = [ur.Text(label)] + [ur.RadioButton(self.group, option, False, self._set_selection) for option in option_list]
		super(SelectPile, self).__init__(widget_list, focus_item)

	def __len__(self):
		return self.length

	def reset(self):
		if self.selection != None:
			i = 1
			while i < len(self):
				self[i].set_state(False)
				i += 1
			self.selection = None

	def get_selection(self):
		return self.selection

	def _set_selection(self, button, state):
		if state:
			self.selection = button.label

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
	#form = CommandForm('command', {'Q1':{}, 'Q2':{}})
	ur.MainLoop(FormListBox(form), palette).run()
	print form

if __name__ == '__main__':
	__main__()

