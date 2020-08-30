# Import internal functions
from functions import R, W, Y, G
from functions import mapping_domain

# Import internal modules
from modules import tuga_certspotter
from modules import tuga_crt
from modules import tuga_hackertarget
from modules import tuga_threatcrowd
from modules import tuga_virustotal
from modules import tuga_entrust
from modules import tuga_googlesearch

# Import BruteForce tugascan
from tugascan import TugaBruteScan
from lib.bscan import bscan_dns_queries
from lib.bscan import bscan_whois_look

class modules:
    def __init__(self, target, enum):

        self.target = target
        self.enum = enum

    def module_choose(self, target ,enum, savemap):

        try:

            bscan_dns_queries(self.target)
            bscan_whois_look(self.target)

            # <Module required> Perform enumerations and network mapping

            supported_engines = {'certspotter': tuga_certspotter.Certspotter,
                                 'hackertarget': tuga_hackertarget.Hackertarget,
                                 'virustotal': tuga_virustotal.Virustotal,
                                 'threatcrowd': tuga_threatcrowd.Threatcrowd,
                                 'ssl': tuga_crt.CRT,
                                 'entrust': tuga_entrust.Entrust,
                                 'googlesearch': tuga_googlesearch.GoogleSearch

                             }
            chosenEnums = []

            if enum is None:
                queries(target)
                chosenEnums = [tuga_certspotter.Certspotter, tuga_hackertarget.Hackertarget, tuga_virustotal.Virustotal,
                               tuga_threatcrowd.Threatcrowd, tuga_crt.CRT, tuga_entrust.Entrust]

                # Start super fast enumeration
                enums = [indicate(target, output) for indicate in chosenEnums]

            else:

                for engine in enum:
                    if engine.lower() in supported_engines:
                        chosenEnums.append(supported_engines[engine.lower()])
                        # Start the enumeration

                        enums = [indicate(target, output) for indicate in chosenEnums]

            # Save map domain (png file)

            if savemap is not False:
                mapping_domain(target)
        except KeyboardInterrupt:
            print("\nTugaRecon interrupted by user\n")
            sys.exit()
