# How to update the website

This is the whole manual. There are five things you will ever need to do, and
each one is a page or two below.

You do not need to install anything. Everything happens in a web browser, on
the website where the site is kept. You will need a free account there and to
be invited once. After that it is just typing and saving.

The site updates itself about a minute after you save. There is nothing to
press, publish, or upload afterwards.

**Nothing you do here can break the site permanently.** Every change is kept,
and any change can be undone. If something looks wrong, it can be put back
exactly as it was.

---

## 1. Add a new Desert Whispers issue

This is the one you will do most, twice a month.

**Name the file first.** This is the only part that matters, and the whole
system depends on it. The file must be named as the date it was published,
year first:

    2026-10-01.pdf          for the October 1 issue
    2026-10-15.pdf          for the October 15 issue
    2026-11-01.pdf          for the November 1 issue

Four digits for the year, a dash, two digits for the month, a dash, two
digits for the day, then `.pdf`. October is `10`, not `Oct` and not `1O`.
The first of the month is `01`, not `1`.

**Then put it in the right folder.**

1. Go to the site's file page in your browser.
2. Open the `documents` folder, then `desert-whispers`, then the folder for
   the year. If it is a new year, there is a note at the bottom of this page
   about making one.
3. Click **Add file**, then **Upload files**.
4. Drag the PDF in, or click to choose it.
5. Scroll down and click **Commit changes**.

That is it. About a minute later the issue appears on the Desert Whispers
page, in the right year, with the date written out properly. You do not have
to type the date anywhere.

---

## 2. Add board meeting minutes

Exactly the same as above, with two differences.

**The folder** is `documents`, then `minutes`, then the year.

**The name** is the date of the meeting:

    2026-10-13.pdf

If the meeting was anything other than a regular monthly meeting, add a word
to the end and it will be labelled on the site automatically:

    2026-10-13-special.pdf              shows as Special Meeting
    2026-10-13-budget.pdf               shows as Budget Meeting
    2026-10-13-budget-committee.pdf     shows as Budget Committee Meeting
    2026-10-13-revised.pdf              shows as Regular Meeting (Revised)
    2026-10-13-attachments.pdf          shows as Attachments

Anything else you put there will simply be ignored, and the minutes will show
as a regular meeting.

---

## 3. Change the events list

The events on the Events page live in one file, written in plain words.

1. Go to the `content` folder.
2. Click `events.yml`.
3. Click the pencil icon to edit it.
4. Change the words, then scroll down and click **Commit changes**.

Each event looks like this:

    - date: "13 Oct"
      title: "Park & Recreation Board Meeting"
      text: "The monthly public meeting of the District Board."
      where: "Community Hall"
      time: "9:00 a.m."

**To change an event,** type over the words inside the quote marks.

**To remove an event,** delete all five of its lines, including the line that
starts with the dash.

**To add an event,** copy an existing block, paste it, and change the words.

Three rules, and they are the only ones:

- Keep the quote marks around the text.
- Keep the spaces at the start of each line exactly as they are. The dash goes
  in front of `date` only.
- Leave a blank line between events.

Put events in order, soonest first. If a time varies, leave the quote marks
empty like this: `time: ""`

---

## 4. Put a notice across the top of the site

Use this when the lake freezes, the course closes, or a meeting is cancelled.

1. Go to `content`, then `status.yml`, and click the pencil icon.
2. Change `show: false` to `show: true`.
3. Type the message in the `text` line.
4. Click **Commit changes**.

To take it down, change `show: true` back to `show: false`. Do take it down
when it stops being true, or people stop reading it.

---

## 5. Change the board roster

After an election.

1. Go to `content`, then `board.yml`, and click the pencil icon.
2. Type over the names and roles.
3. Click **Commit changes**.

Each person looks like this:

    - name: "Scott Batson"
      role: "Chairperson"
      phone: "(458) 281-5925"

If a phone number is not published, delete the whole `phone` line. To add a
person, copy a block and change the words. To remove someone, delete their
block including the dash line.

---

## If something goes wrong

**The issue did not appear after a few minutes.**
Almost always the file name. Check it against the examples above. The three
most common mistakes are a month written as a word, a missing leading zero,
and a space somewhere in the name. Rename the file and upload it again.

**A page looks broken after editing a content file.**
Something in the spacing or the quote marks. Go back to that file, click the
clock or History icon, find the version from before your change, and restore
it. Nothing is lost.

**You want to check whether it worked.**
Every rebuild leaves a record under the Actions tab. A green check means it
ran. A red X means it stopped, and clicking it shows the reason in plain
English, usually naming the exact file.

**Still stuck.** Call or email, and it can be sorted out in a few minutes.
Nothing you did is permanent and nothing is lost.

---

## Starting a new year

The first issue of a new year needs a folder for that year.

When you are in `documents/desert-whispers` and click **Add file**, then
**Create new file**, type the year, then a slash, then the file name:

    2027/2027-01-01.pdf

Typing the slash makes the folder. You only do this once a year, for the first
issue and the first set of minutes.

---

## What this does not cover

Golf rates, hall rental rates, the advertising rate card, facility details and
the wording on the main pages are not in the content files yet. Those change
rarely. Ask and they can either be changed for you or moved into a content
file like the ones above.
