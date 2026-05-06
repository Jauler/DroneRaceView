RH_SRC ?= /home/t1315/source/RotorHazard
RH_STATIC := $(RH_SRC)/src/server/static
DEST := static/_rh

DIRS := jquery-3.6.4 articulate socket.io-4.6.1 smoothie magnific-1.1.0 image
FILES := svgasset.js rotorhazard.js rh-ui.js stream.css

.PHONY: sync-rh
sync-rh:
	@if [ ! -d "$(RH_STATIC)" ]; then \
	  echo "RH_STATIC not found at $(RH_STATIC). Set RH_SRC=/path/to/RotorHazard" >&2; \
	  exit 1; \
	fi
	@mkdir -p $(DEST)
	@for d in $(DIRS); do \
	  rm -rf $(DEST)/$$d; \
	  cp -r $(RH_STATIC)/$$d $(DEST)/$$d; \
	done
	@for f in $(FILES); do \
	  cp $(RH_STATIC)/$$f $(DEST)/$$f; \
	done
	@echo "Synced RH static from $(RH_STATIC) into $(DEST)"
