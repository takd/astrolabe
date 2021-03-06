#!/usr/bin/python3
# climate.py
# -*- coding: utf-8 -*-
#
# The python script in this file makes the various parts of a model astrolabe.
#
# Copyright (C) 2010-2019 Dominic Ford <dcf21-www@dcford.org.uk>
#
# This code is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# You should have received a copy of the GNU General Public License along with
# this file; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

# ----------------------------------------------------------------------------

"""
Render the climate of the astrolabe.
"""

import re
from math import pi, sin, tan, cos, atan2, hypot, acos

from constants import unit_deg, unit_cm, unit_mm, inclination_ecliptic, centre_scaling, r_1, d_12, tab_size
from graphics_context import BaseComponent
from text import text
from numpy import arange
from settings import fetch_command_line_arguments
from themes import themes


class Climate(BaseComponent):
    """
    Render the climate of the astrolabe.
    """

    def default_filename(self):
        """
        Return the default filename to use when saving this component.
        """
        return "climate"

    def bounding_box(self, settings):
        """
        Return the bounding box of the canvas area used by this component.

        :param settings:
            A dictionary of settings required by the renderer.
        :return:
            Dictionary with the elements 'x_min', 'x_max', 'y_min' and 'y_max' set
        """

        r_outer = r_1 - d_12 * 2.5

        return {
            'x_min': -r_outer,
            'x_max': r_outer,
            'y_min': -r_outer,
            'y_max': r_outer
        }

    def do_rendering(self, settings, context):
        """
        This method is required to actually render this item.

        :param settings:
            A dictionary of settings required by the renderer.
        :param context:
            A GraphicsContext object to use for drawing
        :return:
            None
        """

        is_southern = settings['latitude'] < 0
        latitude = abs(settings['latitude'])
        language = settings['language']
        theme = themes[settings['theme']]

        context.set_color(color=theme['lines'])

        context.set_font_size(0.8)

        # The radius of the tab at the top of climate, relative to the centre of the astrolabe
        r_tab = r_1 - d_12 * 2.5 - unit_mm

        # Outer radius of climate
        r_2 = r_1 - d_12 * 3 - unit_mm

        # Radius of central hole
        r_3 = d_12 * centre_scaling

        r_4 = r_2 * tan((90 - inclination_ecliptic) / 2 * unit_deg)
        r_5 = r_4 * tan((90 - inclination_ecliptic) / 2 * unit_deg)

        # Draw the outer edge of climate
        context.begin_path()
        context.circle(centre_x=0, centre_y=0, radius=r_2)
        context.begin_sub_path()
        context.circle(centre_x=0, centre_y=0, radius=r_3)
        context.stroke()
        context.clip()

        # Draw the equator
        context.begin_path()
        context.circle(centre_x=0, centre_y=0, radius=r_4)
        context.stroke()

        # Draw the tropic of Cancer
        context.begin_path()
        context.circle(centre_x=0, centre_y=0, radius=r_5)
        context.stroke()

        # Make the tab at the top of the climate
        context.begin_path()
        context.arc(centre_x=0, centre_y=0, radius=r_tab,
                    arc_from=-tab_size - pi / 2, arc_to=tab_size - pi / 2)
        context.move_to(x=r_tab * sin(tab_size), y=-r_tab * cos(tab_size))
        context.line_to(x=r_2 * sin(tab_size), y=-r_2 * cos(tab_size))
        context.move_to(x=-r_tab * sin(tab_size), y=-r_tab * cos(tab_size))
        context.line_to(x=-r_2 * sin(tab_size), y=-r_2 * cos(tab_size))
        context.stroke()

        # Draw lines of constant altitude
        context.set_font_style(bold=True)
        for altitude in [-6, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]:
            theta1 = (-latitude - (90 - altitude)) * unit_deg
            theta2 = (-latitude + (90 - altitude)) * unit_deg

            x1 = r_4 * sin(theta1)
            y1 = r_4 * cos(theta1)
            x2 = r_4 * sin(theta2)
            y2 = r_4 * cos(theta2)

            y_a = y1 * (r_4 / (r_4 - x1))
            y_b = y2 * (r_4 / (r_4 - x2))

            # Record centre and radius of the arc denoting the horizon
            if altitude == 0:
                horizon_centre = (y_a + y_b) / 2
                horizon_radius = (y_b - y_a) / 2

            if y_b < r_2:
                start = 0
                end = 360 * unit_deg
                if (altitude % 10) == 0:
                    context.text(text="{:d}".format(altitude), x=0, y=-y_b, h_align=0, v_align=1, gap=0, rotation=0)
            else:
                r = (y_b - y_a) / 2
                y = (y_a + y_b) / 2
                start = 180 * unit_deg - acos(
                    (r ** 2 + y ** 2 - r_2 ** 2) / (2 * ((y_b - y_a) / 2) * ((y_a + y_b) / 2)))
                end = -start
                if (altitude > 0) and (altitude % 10 == 0):
                    context.text(text="{:d}".format(altitude),
                                 x=r * sin(start + (r_2 / r) * 2 * unit_deg),
                                 y=-(y_a + y_b) / 2 - r * cos(start + (r_2 / r) * 3 * unit_deg),
                                 h_align=0, v_align=0,
                                 gap=0,
                                 rotation=180 * unit_deg + (start + (r_2 / r) * 3 * unit_deg))
                    context.text(text="{:d}".format(altitude),
                                 x=r * sin(end - (r_2 / r) * 2 * unit_deg),
                                 y=-(y_a + y_b) / 2 - r * cos(end - (r_2 / r) * 3 * unit_deg),
                                 h_align=0, v_align=0,
                                 gap=0,
                                 rotation=180 * unit_deg + (end - (r_2 / r) * 3 * unit_deg))

            context.begin_path()
            context.circle(centre_x=0, centre_y=-(y_a + y_b) / 2, radius=(y_b - y_a) / 2)
            context.stroke(dotted=(altitude < 0),
                           line_width=0.6 + 1.2 * int(altitude == 0),
                           color=theme['alt_az'] if altitude > 0 else theme['lines'])

        # Find coordinates of P
        theta = -latitude * unit_deg
        p_x = r_4 * sin(theta)
        p_y = r_4 * cos(theta)

        # Find coordinates of Z
        z_x = 0
        z_y = p_y / (r_4 - p_x) * r_4

        # Find midpoint between Z and H
        zh_x = -r_4 / 2
        zh_y = z_y / 2

        # Find bearing of T from ZH (clockwise from right-going axis)
        theta = atan2(z_x - (-r_4), z_y)

        # Find coordinates of T
        t_x = 0
        t_y = zh_y + zh_x * tan(theta)

        # Draw lines of constant azimuth
        ss = 11.25 * unit_deg
        altitude = -90 * unit_deg + ss
        for direction in ["", "NNW", "", "NW", "", "WNW", "", "W", "", "WSW", "", "SW", "", "SSW", ""]:
            if is_southern:
                direction = re.sub("N", "s", direction)
                direction = re.sub("S", "N", direction)
                direction = re.sub("s", "S", direction)
                direction = re.sub("W", "e", direction)
                direction = re.sub("E", "W", direction)
                direction = re.sub("e", "E", direction)
            if language == "hu":
                direction = re.sub("N", "É", direction)
                direction = re.sub("W", "Ny", direction)
                direction = re.sub("E", "K", direction)
                direction = re.sub("S", "D", direction)

            t_x = (z_y - t_y) * tan(altitude)

            # Radius of arc of constant azimuth
            t_r = hypot(t_x, t_y - z_y)

            t_hc = hypot(t_x, t_y - horizon_centre)  # Distance from T to centre of horizon
            theta = acos((t_r ** 2 + t_hc ** 2 - horizon_radius ** 2) / (2 * t_r * t_hc))
            phi = atan2(t_x, horizon_centre - t_y)
            start = -phi - theta
            end = -phi + theta

            t_c = hypot(t_x, t_y)  # Distance from T to centre of the astrolabe
            arg = (t_r ** 2 + t_c ** 2 - r_2 ** 2) / (2 * t_r * t_c)
            if (arg >= 1) or (arg <= -1):
                start2 = start
                end2 = end
            else:
                theta = acos((t_r ** 2 + t_c ** 2 - r_2 ** 2) / (2 * t_r * t_c))
                phi = atan2(t_x, -t_y)
                start2 = -phi - theta
                end2 = -phi + theta

            context.begin_path()
            context.arc(centre_x=t_x, centre_y=-t_y, radius=t_r,
                        arc_from=max(start, start2) - pi / 2, arc_to=min(end, end2) - pi / 2)
            context.stroke(line_width=0.5,
                           color=theme['alt_az'])

            context.set_font_style(bold=True)
            context.set_color(theme['text'])
            if hypot(t_x + t_r * sin(end), t_y + t_r * cos(end)) < 0.9 * r_2:
                context.text(text=direction,
                             x=t_x + t_r * sin(end), y=-t_y - t_r * cos(end),
                             h_align=0, v_align=1, gap=unit_mm,
                             rotation=end - 90 * unit_deg)
            else:
                context.text(text=direction,
                             x=t_x + t_r * sin(min(end, end2) - (r_2 / t_r) * 8 * unit_deg),
                             y=-t_y - t_r * cos(min(end, end2) - (r_2 / t_r) * 8 * unit_deg),
                             h_align=0, v_align=0, gap=0,
                             rotation=(min(end, end2) - (r_2 / t_r) * 8 * unit_deg))

            if language != "hu":
                direction = re.sub("N", "s", direction)
                direction = re.sub("S", "N", direction)
                direction = re.sub("s", "S", direction)
                direction = re.sub("W", "e", direction)
                direction = re.sub("E", "W", direction)
                direction = re.sub("e", "E", direction)
            else:    
                direction = re.sub("É", "d", direction)
                direction = re.sub("D", "É", direction)
                direction = re.sub("d", "D", direction)
                direction = re.sub("Ny", "k", direction)
                direction = re.sub("K", "Ny", direction)
                direction = re.sub("k", "K", direction)


            if hypot(t_x + t_r * sin(start), t_y + t_r * cos(start)) < 0.9 * r_2:
                context.text(text=direction,
                             x=t_x + t_r * sin(start),
                             y=-t_y - t_r * cos(start),
                             h_align=0, v_align=1, gap=unit_mm,
                             rotation=90 * unit_deg + start)
            else:
                context.text(text=direction,
                             x=t_x + t_r * sin(max(start, start2) + (r_2 / t_r) * 8 * unit_deg),
                             y=-t_y - t_r * cos(max(start, start2) + (r_2 / t_r) * 8 * unit_deg),
                             h_align=0, v_align=0, gap=0,
                             rotation=(max(start, start2) + (r_2 / t_r) * 8 * unit_deg))

            altitude = altitude + ss


        if language != "hu":
            north_letter = "N"
            south_letter = "S"
        else:
            north_letter = "É"
            south_letter = "D"

        if not is_southern:
            context.text(text=north_letter,
                         x=0, y=-horizon_centre + horizon_radius,
                         h_align=0, v_align=1, gap=unit_mm, rotation=0)
        else:
            context.text(text=south_letter,
                         x=0, y=-horizon_centre + horizon_radius,
                         h_align=0, v_align=1, gap=unit_mm, rotation=0)

        # Subroutine for calculating the azimuthal angle of the lines of the unequal hours
        def theta_unequal_hours(r):
            arg = (r ** 2 + horizon_centre ** 2 - horizon_radius ** 2) / (2 * r * horizon_centre)
            if arg <= -1:
                return 180 * unit_deg
            if arg >= 1:
                return 0 * unit_deg
            return acos(arg)

        # Draw lines of unequal hours below the horizon
        for h in range(1, 12):
            for r in arange(max(r_5, horizon_radius - horizon_centre), r_2 + 0.05 * unit_mm, 0.5 * unit_mm):
                r0 = r
                r1 = min(r + 0.5 * unit_mm, r_2)
                theta0 = theta_unequal_hours(r0)
                theta1 = theta_unequal_hours(r1)
                psi0 = theta0 + (360 * unit_deg - 2 * theta0) / 12 * h
                psi1 = theta1 + (360 * unit_deg - 2 * theta1) / 12 * h
                context.begin_path()
                context.move_to(x=r0 * sin(psi0), y=-r0 * cos(psi0))
                context.line_to(x=r1 * sin(psi1), y=-r1 * cos(psi1))
                context.stroke(line_width=1, dotted=False, color=theme['lines'])

        # Label the unequal hours
        context.set_font_size(1.6)
        h = 0.5
        r = r_2 - 4 * unit_mm
        theta0 = theta_unequal_hours(r)
        context.set_font_style(bold=False)
        for hr in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]:
            psi0 = theta0 + (360 * unit_deg - 2 * theta0) / 12 * h
            psi0 = (psi0 - 180 * unit_deg) * 0.95 + 180 * unit_deg
            context.text(text=hr,
                         x=r * sin(psi0), y=-r * cos(psi0),
                         h_align=0, v_align=0, gap=unit_mm,
                         rotation=180 * unit_deg + psi0)
            h = h + 1

        # White out r_3
        context.begin_path()
        context.move_to(x=-r_2, y=0)
        context.line_to(x=r_2, y=0)
        context.move_to(x=0, y=r_2)
        context.line_to(x=0, y=-r_2)
        context.stroke(line_width=1, dotted=False)

        # Finish up
        context.set_font_style(bold=False)
        context.circular_text(text=text[language]['url'],
                              centre_x=0, centre_y=0, radius=r_2 - 1.6 * unit_cm,
                              azimuth=270, spacing=1, size=0.7)
        context.circular_text(text=text[language]['copyright'],
                              centre_x=0, centre_y=0, radius=r_2 - 1.3 * unit_cm,
                              azimuth=270, spacing=1, size=0.7)
        context.circular_text(text=text[language]['climate_latitude'].format(latitude, north_letter if not is_southern else south_letter),
                              centre_x=0, centre_y=0, radius=r_2 - 1.0 * unit_cm,
                              azimuth=270, spacing=1, size=0.7)


# Do it right away if we're run as a script
if __name__ == "__main__":
    # Fetch command line arguments passed to us
    arguments = fetch_command_line_arguments(default_filename=Climate().default_filename())

    # Render the climate
    Climate(settings={
        'latitude': arguments['latitude'],
        'language': 'en'
    }).render_to_file(
        filename=arguments['filename'],
        img_format=arguments['img_format']
    )
