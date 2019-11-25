###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ContextMenuWdg","DropdownMenuWdg","SubMenuWdg"]

from pyasm.web import *
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg


class SubMenuWdg(BaseRefreshWdg):

    '''Container widget contains a menu.
    @usage
    ctx_menu = SubMenuWdg(menu_id="menuIdLabel",width=55,opt_spec_list=[{}])
    '''

    def __init__(self, **kwargs):

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs
               
        # required args
        self.menu_id = kwargs['menu_id']
        self.width = kwargs['width']
        if not self.width:
            self.width = 200;
        self.opt_spec_list = kwargs['opt_spec_list']

        self.allow_icons = True
        if 'allow_icons' in kwargs:
            self.allow_icons = kwargs['allow_icons']


    def get_args_keys(self):
        return {
            'menu_id': 'The id of the top widget',
            'width': 'The total width (in pixels) for the menu',
            'opt_spec_list': 'Array of dictionaries, with each dict specifying each option on the menu',
            'allow_icons': 'This defaults to True; if False then the left column for icons is not generated'
        }


    def handle_args(self, kwargs):
        # verify the args
        args_keys = self.get_args_keys()
        for key in kwargs.keys():
            if key not in args_keys:
                #raise WidgetException("Key [%s] not in accepted arguments" % key)
                pass

        web = WebContainer.get_web()
        args_keys = self.get_args_keys()
        for key in args_keys.keys():
            if key not in kwargs:
                value = web.get_form_value(key)
                kwargs[key] = value


    def get_menu_id(self):
        return self.menu_id


    def get_display(self):

        menu_div = DivWdg()
        menu_div.set_attr( "id", self.menu_id )
        menu_div.add_class( "SPT_CTX_MENU" )
        menu_div.add_class( "SPT_PUW" )  # make it a Page Utility Widget (now processed client side)

        menu_div.set_z_start( 300 )
        menu_div.add_looks( "menu border curs_default" )

        m_width = self.width - 2
        menu_div.add_style( ("width: %spx" % m_width) )

        menu_table = Table()
        menu_table.add_styles( "text-align: left; text-indent: 3px; border-collapse: collapse;" )

        options = self.opt_spec_list
        for opt in options:

            tbody = menu_table.add_tbody()
            tbody.add_style("display","table-row-group")

            tr = menu_table.add_row()
            tr.add_looks( "menu" )
            tr.add_class( "SPT_CTX_MENU_%s" % opt['type'].upper() )
            disabled = False

            if opt.get('disabled'):
                disabled = True

            if not disabled:
                if opt['type'] in [ 'action', 'toggle' ]:
                    tr.add_behavior( {'type':'hover',
                                      'cbfn_over': 'spt.ctx_menu.entry_over',
                                      'cbfn_out': 'spt.ctx_menu.entry_out',
                                      'hover_class':'look_menu_hover'} )

                if opt['type'] == 'action':
                    if 'bvr_cb' in opt and isinstance(opt['bvr_cb'], dict):
                        bvr = opt['bvr_cb']
                        bvr['cbjs_preaction'] = 'spt.ctx_menu.clear();'
                        # bvr['cbfn_preaction'] = 'spt.ctx_menu.clear'
                        bvr.update( { 'type': 'click', 'mouse_btn': 'LMB' } )
                        tr.add_behavior( bvr )

                if opt['type'] == 'submenu':
                    bvr = { 'type': 'hover',
                            'cbfn_over': 'spt.ctx_menu.submenu_entry_over',
                            'cbfn_out': 'spt.ctx_menu.submenu_entry_out',
                            'hover_class':'look_menu_hover',
                            'options': { 'menu_id': opt['submenu_id'] } }
                    tr.add_behavior( bvr )
                    # now trap click on submenu, so that it doesn't make the current menu disappear ...
                    tr.add_behavior( { 'type': 'click', 'cbjs_action': ';', 'activator_type': 'ctx_menu' } )

            tr.add_looks( "curs_default" )

            icon_width = 16
            icon_col_width = 0

            # Left icon cell ...
            if self.allow_icons:
                td = menu_table.add_cell()
                icon_col_width = icon_width + 2
                td.add_styles("text-align: center; vertical-align: middle; width: %spx;" % icon_col_width)
                td.add_looks("menu_icon_column")

                if 'icon' in opt:
                    icon_wdg = IconWdg("", opt['icon'])
                    td.add( icon_wdg )
                    if disabled:
                        icon_wdg.add_style( "opacity: .4" )
                        icon_wdg.add_style( "filter: alpha(opacity=40)" )

            # Menu option label cell ...
            td = menu_table.add_cell()
            w = m_width - icon_col_width - icon_width
            td.add_style("width", ("%spx" % w))
            td.add_style("height", ("%spx" % icon_col_width))
            td.add_style( "padding-left: 4px" )
            td.add_style( "padding-top: 2px" )
            td.add_style( "cursor: default" )

            label_str = ''
            if 'label' in opt:
                label_str = opt.get('label')
            elif opt.get('type') == 'separator':
                label_str = '<HR>'

            td.add_looks("fnt_text")
            if opt.get('type') == 'title':
                td.add_looks("fnt_bold")

            td.add(label_str)

            if disabled:
                td.add_style( "opacity: .2" )
                td.add_style( "filter: alpha(opacity=20)" )

            # Submenu arrow icon cell ...
            td = menu_table.add_cell()
            td.add_style("width", ("%spx" % icon_width))

            if opt['type'] == 'submenu':
                icon_wdg = IconWdg("", IconWdg.ARROWHEAD_DARK_RIGHT)
                td.add(icon_wdg)

            if disabled:
                td.add_style( "opacity: .4" )
                td.add_style( "filter: alpha(opacity=40)" )

        menu_div.add( menu_table )
        menu_div.add_style( "display: none" )
        menu_div.add_style( "position: absolute" )
        return menu_div


class ContextMenuWdg(SubMenuWdg):

    def __init__(self, **kwargs):
        # call base class constructor first ...
        super(ContextMenuWdg,self).__init__(**kwargs)
        self.activator_wdg = kwargs['activator_wdg']

        self.activator_wdg.add_event( "oncontextmenu",
                                    "return spt.ctx_menu.show_on_context_click_cbk(event,'%s');" % self.menu_id )

    def get_args_keys(self):

        args_keys = {
            'activator_wdg': 'The HTML element widget where the right click occurs to launch the context menu'
        }
        base_args_keys = super(ContextMenuWdg,self).get_args_keys()
        args_keys.update(base_args_keys)
        return args_keys


class DropdownMenuWdg(SubMenuWdg):

    def __init__(self, **kwargs):
        # call base class constructor first ...
        super(DropdownMenuWdg,self).__init__(**kwargs)
        self.activator_wdg = kwargs['activator_wdg']

        bvr = { 'type': 'click_up', 'mouse_btn': 'LMB', 'cbfn_action': 'spt.ctx_menu.show_on_dropdown_click_cbk',
                'activator_type' : 'ctx_menu', 'options': {'menu_id': self.menu_id} }

        self.activator_wdg.add_behavior( bvr )
        self.activator_wdg.add_class('SPT_MENU_ACTIVATOR')


    def get_args_keys(self):

        args_keys = {
            'activator_wdg': 'The HTML element widget where the LMB click occurs to launch the context menu'
        }
        base_args_keys = super(DropdownMenuWdg,self).get_args_keys()
        args_keys.update(base_args_keys)
        return args_keys


