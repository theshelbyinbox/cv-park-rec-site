#!/bin/bash
# Christmas Valley Park & Rec - recover missing PDFs from the Internet Archive
# Safe to run again and again. It only fetches files you don't have yet,
# waits between files so the archive doesn't cut it off, and retries slow ones.
cd "$(dirname "$0")" || exit 1
PAUSE=6
get(){
  [ -s "$2" ] && return 0
  for try in 1 2 3 4; do
    if curl -fsSL --connect-timeout 30 --max-time 900 --create-dirs -o "$2.part" "$1"; then
      mv "$2.part" "$2"; return 0
    fi
    rm -f "$2.part"; sleep $((try*20))
  done
  return 1
}
todo=0; got=0; fail=0; failed=""
run(){
  [ -s "$2" ] && return
  todo=$((todo+1))
  printf "  %-46s " "$2"
  if get "$1" "$2"; then got=$((got+1)); echo "ok"; else fail=$((fail+1)); echo "FAILED"; failed="$failed\n  $2"; fi
  sleep $PAUSE
}
echo ""
echo "Checking for missing files ..."
echo ""
run "https://web.archive.org/web/20170227061723id_/http://cvparkandrec.org/data/documents/DW2016-02-15001.pdf" "documents/desert-whispers/2016/2016-02-15.pdf"
run "https://web.archive.org/web/20170226231630id_/http://cvparkandrec.org/data/documents/DW-2016-03-01web.compressed.pdf" "documents/desert-whispers/2016/2016-03-01.pdf"
run "https://web.archive.org/web/20170227051545id_/http://cvparkandrec.org/data/documents/DW-2016-03-15web2.pdf" "documents/desert-whispers/2016/2016-03-15.pdf"
run "https://web.archive.org/web/20170227054916id_/http://cvparkandrec.org/data/documents/DW-2016-04-01web.pdf" "documents/desert-whispers/2016/2016-04-01.pdf"
run "https://web.archive.org/web/20170227051408id_/http://cvparkandrec.org/data/documents/DW-2016-04-15web.pdf" "documents/desert-whispers/2016/2016-04-15.pdf"
run "https://web.archive.org/web/20170227062132id_/http://cvparkandrec.org/data/documents/DW-2016-05-01web.pdf" "documents/desert-whispers/2016/2016-05-01.pdf"
run "https://web.archive.org/web/20160528003606id_/http://cvparkandrec.org/data/documents/DW-2016-05-15web.pdf" "documents/desert-whispers/2016/2016-05-15.pdf"
run "https://web.archive.org/web/20170226233633id_/http://cvparkandrec.org/data/documents/DW-2016-06-01web.pdf" "documents/desert-whispers/2016/2016-06-01.pdf"
run "https://web.archive.org/web/20170227062213id_/http://cvparkandrec.org/data/documents/DW-2016-06-15web.pdf" "documents/desert-whispers/2016/2016-06-15.pdf"
run "https://web.archive.org/web/20170227055934id_/http://cvparkandrec.org/data/documents/DW-2016-07-01web_1.pdf" "documents/desert-whispers/2016/2016-07-01.pdf"
run "https://web.archive.org/web/20170227060513id_/http://cvparkandrec.org/data/documents/DW-2016-07-15web.pdf" "documents/desert-whispers/2016/2016-07-15.pdf"
run "https://web.archive.org/web/20170226231500id_/http://cvparkandrec.org/data/documents/DW-2016-08-01web.compressed.pdf" "documents/desert-whispers/2016/2016-08-01.pdf"
run "https://web.archive.org/web/20170227060011id_/http://cvparkandrec.org/data/documents/DW-2016-08-15web.pdf" "documents/desert-whispers/2016/2016-08-15.pdf"
run "https://web.archive.org/web/20170227060310id_/http://cvparkandrec.org/data/documents/DW-2016-09-01web.pdf" "documents/desert-whispers/2016/2016-09-01.pdf"
run "https://web.archive.org/web/20170227062322id_/http://cvparkandrec.org/data/documents/DW-2016-09-15web.pdf" "documents/desert-whispers/2016/2016-09-15.pdf"
run "https://web.archive.org/web/20170226225004id_/http://cvparkandrec.org/data/documents/DW-2016-10-01web.pdf" "documents/desert-whispers/2016/2016-10-01.pdf"
run "https://web.archive.org/web/20170226231930id_/http://cvparkandrec.org/data/documents/DW-2016-10-15web.pdf" "documents/desert-whispers/2016/2016-10-15.pdf"
run "https://web.archive.org/web/20170227174901id_/http://cvparkandrec.org/data/documents/CVG-1962-7JUL.pdf" "documents/gazette/1962/1962-07.pdf"
run "https://web.archive.org/web/20170228001243id_/http://cvparkandrec.org/data/documents/CVG-1962-8AUG.pdf" "documents/gazette/1962/1962-08.pdf"
run "https://web.archive.org/web/20170228012542id_/http://cvparkandrec.org/data/documents/CVG-1962-Special001.pdf" "documents/gazette/1962/1962-special-anniversary-issu-special.pdf"
run "https://web.archive.org/web/20170228061145id_/http://cvparkandrec.org/data/documents/CVG-1963-2Feb001.pdf" "documents/gazette/1963/1963-02.pdf"
run "https://web.archive.org/web/20170228011505id_/http://cvparkandrec.org/data/documents/CVG-1963-3Mar001.pdf" "documents/gazette/1963/1963-03.pdf"
run "https://web.archive.org/web/20170227184023id_/http://cvparkandrec.org/data/documents/CVG-1963-04APR001.pdf" "documents/gazette/1963/1963-04.pdf"
run "https://web.archive.org/web/20170228061127id_/http://cvparkandrec.org/data/documents/CVG-1963-05MAY001.pdf" "documents/gazette/1963/1963-05.pdf"
run "https://web.archive.org/web/20170228061134id_/http://cvparkandrec.org/data/documents/CVG-1963-06JUN001.pdf" "documents/gazette/1963/1963-06.pdf"
run "https://web.archive.org/web/20170227184106id_/http://cvparkandrec.org/data/documents/CVG-1963-08AUG001.pdf" "documents/gazette/1963/1963-08.pdf"
run "https://web.archive.org/web/20170227185656id_/http://cvparkandrec.org/data/documents/CVG-1963-09SEP001.pdf" "documents/gazette/1963/1963-09.pdf"
run "https://web.archive.org/web/20170227180427id_/http://cvparkandrec.org/data/documents/CVG-1963-10OCT001.pdf" "documents/gazette/1963/1963-10-anniversary.pdf"
run "https://web.archive.org/web/20170226231054id_/http://cvparkandrec.org/data/documents/CVG-1967-FEB001.pdf" "documents/gazette/1967/1967-02.pdf"
run "https://web.archive.org/web/20170227062528id_/http://cvparkandrec.org/data/documents/CVG-1967-MARAPR001.pdf" "documents/gazette/1967/1967-04.pdf"
run "https://web.archive.org/web/20170227054137id_/http://cvparkandrec.org/data/documents/CVG-1967-JULY001.pdf" "documents/gazette/1967/1967-07.pdf"
run "https://web.archive.org/web/20170226232007id_/http://cvparkandrec.org/data/documents/CVG-1967-AUGSEPT001.pdf" "documents/gazette/1967/1967-09.pdf"
run "https://web.archive.org/web/20170226231832id_/http://cvparkandrec.org/data/documents/CVG-DEC1966JAN1967001.pdf" "documents/gazette/1967/1967-12.pdf"
run "https://web.archive.org/web/20170227045929id_/http://cvparkandrec.org/data/documents/2016-02-09-Meeting-minutes.pdf" "documents/minutes/2016/2016-02-09.pdf"
run "https://web.archive.org/web/20170227053421id_/http://cvparkandrec.org/data/documents/2016-03-02-Meeting-minutes.pdf" "documents/minutes/2016/2016-03-02.pdf"
run "https://web.archive.org/web/20170226225350id_/http://cvparkandrec.org/data/documents/2016-04-12-Regular-Budget-Meeting-minutes.pdf" "documents/minutes/2016/2016-04-12-budget-committee.pdf"
run "https://web.archive.org/web/20170227055021id_/http://cvparkandrec.org/data/documents/2016-04-12-Supplemental-Budget-Meeting-minutes.pdf" "documents/minutes/2016/2016-04-12-supplemental-budget.pdf"
run "https://web.archive.org/web/20170227053428id_/http://cvparkandrec.org/data/documents/2016-04-12-Meeting-minutes.pdf" "documents/minutes/2016/2016-04-12.pdf"
run "https://web.archive.org/web/20170227054520id_/http://cvparkandrec.org/data/documents/2016-05-10-Budget-Committee-Meeting-minutes.pdf" "documents/minutes/2016/2016-05-10-budget-committee.pdf"
run "https://web.archive.org/web/20170227000555id_/http://cvparkandrec.org/data/documents/2016-05-10-Meeting-minutes.pdf" "documents/minutes/2016/2016-05-10.pdf"
run "https://web.archive.org/web/20170226224547id_/http://cvparkandrec.org/data/documents/2016-06-14-Meeting-minutes.pdf" "documents/minutes/2016/2016-06-14.pdf"
run "https://web.archive.org/web/20170226230155id_/http://cvparkandrec.org/data/documents/2016-07-12-Meeting-minutes.pdf" "documents/minutes/2016/2016-07-12.pdf"
run "https://web.archive.org/web/20170226235537id_/http://cvparkandrec.org/data/documents/2016-08-09-Meeting-minutes.pdf" "documents/minutes/2016/2016-08-09.pdf"
run "https://web.archive.org/web/20170227052156id_/http://cvparkandrec.org/data/documents/2016-09-12-Meeting-minutes.pdf" "documents/minutes/2016/2016-09-13.pdf"
echo ""
if [ $todo -eq 0 ]; then echo "Nothing missing - everything is already here."; else
  echo "Tried: $todo   Got: $got   Failed: $fail"
  [ $fail -gt 0 ] && printf "Still missing:$failed\n"
  [ $fail -gt 0 ] && echo "" && echo "Run this file again to retry just those."
fi
echo ""
echo "Done. Tell Claude."
echo "(You can close this window.)"
