--[[
    Xbox to MA3 Controller Plugin
    Optimiert für GrandMA3 Version 2.3.1.1
    
    Dieses Plugin nutzt die korrekten API-Calls für v2.3.1.1
    
    Features:
    - Relativer Modus (Ego-Shooter Style)
    - Absoluter Modus (Direkte Position)
    - Dimmer Control
    - Follow Mode (Einzelnes Fixture zuweisen)
    - Speed Control
    
    Setup:
    1. Python Script muss laufen (sendet OSC)
    2. In MA3: Menu → In & Out → OSC → Port 8000 aktivieren
    3. Plugin importieren und starten
    4. Fixtures selektieren
    5. Controller bewegen!
]]

local pluginName = "XboxControl"
local version = "2.3.1.1"

-- ============================================================================
-- KONFIGURATION
-- ============================================================================

local CONFIG = {
    -- OSC Quelle
    source_page = 1,
    fader_pan = 201,
    fader_tilt = 202,
    fader_dimmer = 203,
    fader_fine_pan = 204,
    fader_fine_tilt = 205,
    
    -- Steuerung
    deadzone = 5,              -- Prozent
    default_mode = "relative", -- "relative" oder "absolute"
    speed_multiplier = 2.0,
    fine_multiplier = 0.3,
    
    -- Performance
    update_interval = 0.05,    -- 20 Hz (50ms)
    show_stats = true,
}

-- ============================================================================
-- GLOBALE VARIABLEN
-- ============================================================================

local currentMode = CONFIG.default_mode
local isRunning = false
local updateCounter = 0
local assignedFixture = nil
local assignMode = false

-- Velocity State für Smoothing
local velocity = {
    pan = 0,
    tilt = 0,
    pan_fine = 0,
    tilt_fine = 0
}

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

local function log(msg)
    Printf("[" .. pluginName .. " v" .. version .. "] " .. tostring(msg))
end

local function applyDeadzone(value, center, deadzone)
    local delta = value - center
    if math.abs(delta) < deadzone then
        return center
    end
    return value
end

local function smoothVelocity(current, target, factor)
    -- Einfache lineare Interpolation
    return current + (target - current) * (1.0 - factor)
end

-- MA3 2.3.1.1 kompatible Fader-Lesung
local function getFaderValue(page, faderId)
    -- Für v2.3.1.1: Nutze GetExecutor
    local execNumber = (page * 100) + faderId
    
    -- Methode 1: GetExecutor (Standard für v2.3.x)
    local success, result = pcall(function()
        local exec = GetExecutor(execNumber)
        if exec then
            -- Fader ist 0-1, wir brauchen 0-100
            return exec.Fader * 100
        end
        return nil
    end)
    
    if success and result then
        return result
    end
    
    -- Methode 2: ShowData Zugriff (Fallback)
    success, result = pcall(function()
        local showdata = ShowData()
        if showdata and showdata.DataPools and showdata.DataPools.Default then
            local exec = showdata.DataPools.Default.Sequences[execNumber]
            if exec and exec.MasterFader then
                return exec.MasterFader * 100
            end
        end
        return nil
    end)
    
    if success and result then
        return result
    end
    
    -- Fallback: Return nil (wird dann übersprungen)
    return nil
end

-- ============================================================================
-- HAUPT UPDATE LOOP
-- ============================================================================

local function updateLoop()
    if not isRunning then
        return
    end
    
    updateCounter = updateCounter + 1
    
    -- Lese Fader-Werte (vom Python Script via OSC gesetzt)
    local panRaw = getFaderValue(CONFIG.source_page, CONFIG.fader_pan)
    local tiltRaw = getFaderValue(CONFIG.source_page, CONFIG.fader_tilt)
    local dimmerRaw = getFaderValue(CONFIG.source_page, CONFIG.fader_dimmer)
    
    -- DEBUG: Zeige erste paar Werte
    if updateCounter <= 5 then
        log(string.format("DEBUG: Pan=%.1f, Tilt=%.1f, Dimmer=%.1f", 
            panRaw or -1, tiltRaw or -1, dimmerRaw or -1))
    end
    
    if not panRaw or not tiltRaw then
        -- Fader nicht verfügbar - Skip
        if updateCounter % 500 == 1 then
            log("WARNUNG: Kann Fader nicht lesen! Prüfe OSC Executors in MA3!")
        end
        return
    end
    
    -- Deadzone anwenden
    local panVal = applyDeadzone(panRaw, 50, CONFIG.deadzone)
    local tiltVal = applyDeadzone(tiltRaw, 50, CONFIG.deadzone)
    
    -- ========================================================================
    -- RELATIVE MODE
    -- ========================================================================
    
    if currentMode == "relative" then
        -- Berechne Velocity (Speed basierend auf Stick-Position)
        local panTarget = (panVal - 50) / 50 * CONFIG.speed_multiplier
        local tiltTarget = (tiltVal - 50) / 50 * CONFIG.speed_multiplier
        
        -- Smooth Velocity (sanfte Beschleunigung)
        velocity.pan = smoothVelocity(velocity.pan, panTarget, 0.2)
        velocity.tilt = smoothVelocity(velocity.tilt, tiltTarget, 0.2)
        
        -- Apply Movement
        if math.abs(velocity.pan) > 0.01 then
            if assignMode and assignedFixture then
                -- Follow Mode: Spezifisches Fixture
                Cmd(string.format("Fixture %d Attribute 'Pan' At %+.2f", assignedFixture, velocity.pan))
            else
                -- Selection Mode
                Cmd(string.format("Attribute 'Pan' At %+.2f", velocity.pan))
            end
        end
        
        if math.abs(velocity.tilt) > 0.01 then
            if assignMode and assignedFixture then
                Cmd(string.format("Fixture %d Attribute 'Tilt' At %+.2f", assignedFixture, velocity.tilt))
            else
                Cmd(string.format("Attribute 'Tilt' At %+.2f", velocity.tilt))
            end
        end
    
    -- ========================================================================
    -- ABSOLUTE MODE  
    -- ========================================================================
    
    elseif currentMode == "absolute" then
        -- Direkte Position Mapping
        local panUser = (panVal - 50) * 2    -- -100 bis +100
        local tiltUser = (tiltVal - 50) * 2
        
        if assignMode and assignedFixture then
            Cmd(string.format("Fixture %d Attribute 'Pan' At %.2f", assignedFixture, panUser))
            Cmd(string.format("Fixture %d Attribute 'Tilt' At %.2f", assignedFixture, tiltUser))
        else
            Cmd(string.format("Attribute 'Pan' At %.2f", panUser))
            Cmd(string.format("Attribute 'Tilt' At %.2f", tiltUser))
        end
    end
    
    -- ========================================================================
    -- FINE CONTROL (Optional - Rechter Stick)
    -- ========================================================================
    
    local panFineRaw = getFaderValue(CONFIG.source_page, CONFIG.fader_fine_pan)
    local tiltFineRaw = getFaderValue(CONFIG.source_page, CONFIG.fader_fine_tilt)
    
    if panFineRaw and tiltFineRaw then
        local panFineVal = applyDeadzone(panFineRaw, 50, CONFIG.deadzone)
        local tiltFineVal = applyDeadzone(tiltFineRaw, 50, CONFIG.deadzone)
        
        local panFineTarget = (panFineVal - 50) / 50 * CONFIG.speed_multiplier * CONFIG.fine_multiplier
        local tiltFineTarget = (tiltFineVal - 50) / 50 * CONFIG.speed_multiplier * CONFIG.fine_multiplier
        
        velocity.pan_fine = smoothVelocity(velocity.pan_fine, panFineTarget, 0.2)
        velocity.tilt_fine = smoothVelocity(velocity.tilt_fine, tiltFineTarget, 0.2)
        
        if math.abs(velocity.pan_fine) > 0.005 then
            if assignMode and assignedFixture then
                Cmd(string.format("Fixture %d Attribute 'Pan' At %+.3f", assignedFixture, velocity.pan_fine))
            else
                Cmd(string.format("Attribute 'Pan' At %+.3f", velocity.pan_fine))
            end
        end
        
        if math.abs(velocity.tilt_fine) > 0.005 then
            if assignMode and assignedFixture then
                Cmd(string.format("Fixture %d Attribute 'Tilt' At %+.3f", assignedFixture, velocity.tilt_fine))
            else
                Cmd(string.format("Attribute 'Tilt' At %+.3f", velocity.tilt_fine))
            end
        end
    end
    
    -- ========================================================================
    -- DIMMER
    -- ========================================================================
    
    if dimmerRaw and dimmerRaw > 5 then
        if assignMode and assignedFixture then
            Cmd(string.format("Fixture %d Attribute 'Dimmer' At %.1f", assignedFixture, dimmerRaw))
        else
            Cmd(string.format("Attribute 'Dimmer' At %.1f", dimmerRaw))
        end
    end
    
    -- Stats
    if CONFIG.show_stats and updateCounter % 200 == 0 then
        local mode_str = assignMode and ("FOLLOW: Fixture " .. assignedFixture) or "SELECTION"
        log(string.format("Updates: %d | Mode: %s | %s", updateCounter, currentMode, mode_str))
    end
end

-- ============================================================================
-- PLUGIN LIFECYCLE
-- ============================================================================

function Main()
    log("╔════════════════════════════════════════════════╗")
    log("║  Xbox Controller Plugin für MA3 v2.3.1.1      ║")
    log("╚════════════════════════════════════════════════╝")
    log("")
    log("Modus:       " .. currentMode)
    log("Speed:       " .. CONFIG.speed_multiplier .. "x")
    log("Deadzone:    " .. CONFIG.deadzone .. "%")
    log("Source:      Page " .. CONFIG.source_page .. ", Fader " .. CONFIG.fader_pan .. "-" .. CONFIG.fader_dimmer)
    log("")
    log("WICHTIG:")
    log("1. Python Script muss laufen (sendet OSC)")
    log("2. OSC Port 8000 in MA3 aktiviert")
    log("3. Fixtures selektieren ODER AssignFixture(id) nutzen")
    log("4. Controller bewegen!")
    log("")
    log("Plugin läuft...")
    
    isRunning = true
    
    -- Haupt-Loop
    while isRunning do
        updateLoop()
        coroutine.yield(CONFIG.update_interval)
    end
    
    log("Plugin beendet")
end

function Cleanup()
    log("Cleanup wird ausgeführt...")
    isRunning = false
    velocity = {pan = 0, tilt = 0, pan_fine = 0, tilt_fine = 0}
end

-- ============================================================================
-- USER COMMANDS
-- ============================================================================

function ToggleMode()
    currentMode = (currentMode == "relative") and "absolute" or "relative"
    log("═══════════════════════════════════════════════")
    log("MODUS GEWECHSELT: " .. currentMode:upper())
    log("═══════════════════════════════════════════════")
    velocity = {pan = 0, tilt = 0, pan_fine = 0, tilt_fine = 0}
end

function SetSpeed(multiplier)
    local newSpeed = tonumber(multiplier)
    if newSpeed and newSpeed > 0 and newSpeed <= 10 then
        CONFIG.speed_multiplier = newSpeed
        log("═══════════════════════════════════════════════")
        log("SPEED: " .. newSpeed .. "x")
        log("═══════════════════════════════════════════════")
    else
        log("FEHLER: Speed muss 0.1 - 10.0 sein")
    end
end

function SetDeadzone(percent)
    local newDZ = tonumber(percent)
    if newDZ and newDZ >= 0 and newDZ <= 50 then
        CONFIG.deadzone = newDZ
        log("═══════════════════════════════════════════════")
        log("DEADZONE: " .. newDZ .. "%")
        log("═══════════════════════════════════════════════")
    else
        log("FEHLER: Deadzone muss 0-50% sein")
    end
end

function AssignFixture(fixtureId)
    local id = tonumber(fixtureId)
    if not id then
        log("FEHLER: Ungültige Fixture ID")
        return
    end
    
    assignedFixture = id
    assignMode = true
    
    log("═══════════════════════════════════════════════")
    log("FOLLOW MODE AKTIV")
    log("═══════════════════════════════════════════════")
    log("Fixture ID:  " .. id)
    log("Modus:       " .. currentMode)
    log("")
    log("Nur dieses Fixture wird jetzt gesteuert!")
    log("Zum Beenden: Lua \"ClearFixture()\"")
    log("═══════════════════════════════════════════════")
end

function ClearFixture()
    if assignedFixture then
        log("Follow Mode beendet (war: Fixture " .. assignedFixture .. ")")
    end
    assignedFixture = nil
    assignMode = false
    log("═══════════════════════════════════════════════")
    log("ZURÜCK ZU SELECTION MODE")
    log("═══════════════════════════════════════════════")
end

function ShowStatus()
    log("═══════════════════════════════════════════════")
    log("STATUS")
    log("═══════════════════════════════════════════════")
    log("Version:     " .. version)
    log("Modus:       " .. currentMode:upper())
    log("Speed:       " .. CONFIG.speed_multiplier .. "x")
    log("Deadzone:    " .. CONFIG.deadzone .. "%")
    log("Updates:     " .. updateCounter)
    log("Running:     " .. tostring(isRunning))
    
    if assignMode and assignedFixture then
        log("Control:     FOLLOW MODE (Fixture " .. assignedFixture .. ")")
    else
        log("Control:     SELECTION MODE")
    end
    
    log("═══════════════════════════════════════════════")
end

-- ============================================================================
-- RETURN
-- ============================================================================

return Main, Cleanup
