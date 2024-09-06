import unrealsdk
from Mods import ModMenu
   
class ScopedSens(ModMenu.SDKMod):
    Name: str = "Custom Scoped Sensitivity"
    Author: str = "Deceptix_"
    Description: str = "Adds custom ADS sensitivity multiplier sliders for each sniper sight."
    Version: str = "1.0.0"
    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadWithSettings
    SupportedGames: ModMenu.Game = ModMenu.Game.BL2 | ModMenu.Game.TPS
    Types: ModMenu.ModTypes = ModMenu.ModTypes.Utility
    
    defaultSens = 60
    adsMultiDahl = 25
    adsMultiVladof = 21
    adsMultiMaliwan = 18
    adsMultiJakobs = 15
    adsMultiHyperion = 12

    def __init__(self) -> None:
        self.DahlSlider = ModMenu.Options.Slider(
            Caption="Dahl Sight Sensitivity Multiplier",
            Description="ADS Sensitivity multiplier for Dahl sights on snipers (in %).\nThis slider will also change snipers with no sight.",
            StartingValue = 25,
            MinValue = 1,
            MaxValue = 100,
            Increment = 1,
        )

        self.VladofSlider = ModMenu.Options.Slider(
            Caption="Vladof Sight Sensitivity Multiplier",
            Description="ADS Sensitivity multiplier for Vladof sights on snipers (in %)",
            StartingValue = 21,
            MinValue = 1,
            MaxValue = 100,
            Increment = 1,
        )

        self.MaliwanSlider = ModMenu.Options.Slider(
            Caption="Maliwan Sight Sensitivity Multiplier",
            Description="ADS Sensitivity multiplier for Maliwan sights on snipers (in %)",
            StartingValue = 18,
            MinValue = 1,
            MaxValue = 100,
            Increment = 1,
        )

        self.JakobsSlider = ModMenu.Options.Slider(
            Caption="Jakobs Sight Sensitivity Multiplier",
            Description="ADS Sensitivity multiplier for Jakobs sights on snipers (in %)",
            StartingValue = 15,
            MinValue = 1,
            MaxValue = 100,
            Increment = 1,
        )

        self.HyperionSlider = ModMenu.Options.Slider(
            Caption="Hyperion Sight Sensitivity Multiplier",
            Description="ADS Sensitivity multiplier for Hyperion sights on snipers (in %)",
            StartingValue = 12,
            MinValue = 1,
            MaxValue = 100,
            Increment = 1,
        )

        self.Options = [
            self.DahlSlider,
            self.VladofSlider,
            self.MaliwanSlider,
            self.JakobsSlider,
            self.HyperionSlider,
        ]

    def ModOptionChanged(self, option: ModMenu.Options.Base, new_value) -> None:
        if option == self.DahlSlider:
                self.adsMultiDahl = new_value
        if option == self.VladofSlider:
                self.adsMultiVladof = new_value
        if option == self.MaliwanSlider:
                self.adsMultiMaliwan = new_value
        if option == self.JakobsSlider:
                self.adsMultiJakobs = new_value
        if option == self.HyperionSlider:
                self.adsMultiHyperion = new_value
    
    @ModMenu.Hook("WillowGame.WillowWeapon.SetZoomState")
    def onADS(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> None:
        WPC = unrealsdk.GetEngine().GamePlayers[0].Actor
        sliderInput = [self.adsMultiDahl, self.adsMultiVladof, self.adsMultiMaliwan, self.adsMultiJakobs, self.adsMultiHyperion]
        manufacturerList = ["Dahl", "Vladof", "Maliwan", "Jakobs", "Hyperion"]
        outlierList = ["HawkEye", "FremingtonsEdge", "Longbow", "ElephantGun", "Buffalo"]

        # Buffalo name is changed in TPS so we need to change the outlier list
        if ModMenu.Game.GetCurrent() == ModMenu.Game.TPS:
            outlierList[4] = "Razorback"

        # I use static values here because I couldnt figure out how to remove Gearbox's ADS sensitivity changes
        # Some specific guns needed their own values so they are listed at the end
        zoomSens = [[3.992, 4.302, 5.258, 6.248, 7.619],        # Dahl
                    [3.755, 4.046, 4.941, 5.868, 7.150],        # Vladof
                    [4.260, 4.593, 5.618, 6.681, 8.151],        # Maliwan
                    [4.565, 4.924, 6.027, 7.173, 8.758],        # Jakobs
                    [4.916, 5.303, 6.497, 7.737, 9.457],        # Hyperion
                    [8.355, 8.758, 9.991, 11.2591, 13.0045],    # HawkEye
                    [0.000, 0.000, 0.000, 0.000, 12.642],       # Fremington's Edge
                    [4.534],                                    # Longbow
                    [7.171],                                    # Elephant Gun
                    [4.212]]                                    # Buffalo / Razorback
        
        sightIndex = 0
        manufacturerIndex = 0

        if params.NewZoomState == 2: # Only changes sensitivity when ADS
            if "Sniper" in str(WPC.Pawn.Weapon.DefinitionData.WeaponTypeDefinition): # Checks if the current held gun is a sniper
                for name in manufacturerList:
                    if name in str(WPC.Pawn.Weapon.DefinitionData.SightPartDefinition): # Finds the sight manufacturer index according to manufacturerList
                        sightIndex = manufacturerList.index(name)
                    if name in str(WPC.Pawn.Weapon.DefinitionData.ManufacturerDefinition): # Finds the gun manufacturer index according to manufacturerList
                        manufacturerIndex = manufacturerList.index(name)
                for name in outlierList:
                    if name in str(WPC.Pawn.Weapon.DefinitionData.BalanceDefinition): # Checks if current gun is one of the outliers
                            manufacturerIndex = 5 + outlierList.index(name) # Updates the index to match the right sensitivity multiplier in zoomSens
                WPC.PlayerInput.MouseSensitivity = self.defaultSens * zoomSens[manufacturerIndex][sightIndex] * (sliderInput[sightIndex] / 100)
                # The goal of the first part of this equation (self.defaultSens * zoomSens[manufacturerIndex][sightIndex]) is to remove the ADS sensitivity multiplier that is set by default.
                # After this we get an ADS sensitivity that is 1:1 to the normal players sensitivity.
                # The last part of the equation (sliderInput[sightIndex] / 100) gives us the sensitivity multiplier that user actually wants for the sight on their current gun
        else:
            WPC.PlayerInput.MouseSensitivity = self.defaultSens # Undo the sensitivity change when not ADS anymore
            
        return True

    def Enable(self) -> None:
        WPC = unrealsdk.GetEngine().GamePlayers[0].Actor
        super().Enable()
        self.defaultSens = WPC.PlayerInput.MouseSensitivity

    def Disable(self) -> None:
        super().Disable()

instance = ScopedSens()
ModMenu.RegisterMod(instance)