# -*- coding: utf-8 -*-

LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 10
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 5
ADJACENT_PAGES = 4


def digg_paginator(cnt, current):
    in_leading_range = in_trailing_range = False
    pages_outside_leading_range = pages_outside_trailing_range = range(0)

    if (cnt <= LEADING_PAGE_RANGE_DISPLAYED):
        in_leading_range = in_trailing_range = True
        page_numbers = [n for n in range(1, cnt + 1) if n > 0 and n <= cnt]
    elif (current <= LEADING_PAGE_RANGE):
        in_leading_range = True
        page_numbers = [n for n in range(
            1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= cnt]
        pages_outside_leading_range = [
            n + cnt for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
    elif (current > cnt - TRAILING_PAGE_RANGE):
        in_trailing_range = True
        page_numbers = [
            n
            for n in range(cnt - TRAILING_PAGE_RANGE_DISPLAYED + 1, cnt + 1)
            if n > 0 and n <= cnt
        ]
        pages_outside_trailing_range = [
            n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    else:
        page_numbers = [
            n
            for n in range(current - ADJACENT_PAGES,
                           current + ADJACENT_PAGES + 1)
            if n > 0 and n <= cnt
        ]
        pages_outside_leading_range = [
            n + cnt for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        pages_outside_trailing_range = [
            n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    return {
        "page_numbers": page_numbers,
        "pages_outside_trailing_range": pages_outside_trailing_range,
        "pages_outside_leading_range": sorted(pages_outside_leading_range)
    }
