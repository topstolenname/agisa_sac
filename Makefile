# Redirect Makefile targets to scripts/Makefile to preserve root DX

.PHONY: %
%:
	$(MAKE) -f scripts/Makefile $@
