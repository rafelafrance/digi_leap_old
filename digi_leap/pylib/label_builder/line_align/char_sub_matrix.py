# # import numpy as np
# from ...db import db
#
#
# def add_chars(args):
#     """Add characters to the character substitution matrix."""
#     with db.connect(args.database) as cxn:
#         run_id = db.insert_run(cxn, args)
#
#         sql = """select * from char_sub_matrix where char_set = ?"""
#         rows = db.execute(cxn, sql, (args.char_set,))
#         rows = {(r["char1"], r["char2"]): dict(r) for r in rows}
#
#         old_chars = {k[0] for k in rows.keys()}
#         old_chars |= {k[1] for k in rows.keys()}
#         old_chars = sorted(old_chars)
#
#         new_chars = sorted(args.chars)
#
#         db.update_run_finished(cxn, run_id)
#
#
# def build_matrix(all_chars, new_chars, rows):
#     for i, char1 in enumerate(all_chars):
#         for char2 in all_chars[i:]:
#             if char1 not in new_chars and char2 not in new_chars:
#                 score = rows[(char1, char2)]["score"]
#             if char1 == char2:
#                 score = 1.0
#             elif char1 == " ":
#                 ...
#             else:
#                 ...
#
#
# def iou_space(char2, image_size, font):
#     """Get how many pixels the character occupies."""
#     image2 = Image.new("L", (image_size, image_size), color="black")
#     draw2 = ImageDraw.Draw(image2)
#     draw2.text((0, 0), char2, font=font, anchor="lt", fill="white")
#
#     data2 = np.asarray(image2) > 128
#     data2 = data2.astype("float")
#     inter = np.sum(data2)
#     return inter
