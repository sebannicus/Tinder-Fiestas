// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ProofOfPresence
 * @dev Registro inmutable de asistencia a eventos con validaciones y estadísticas
 * @author Tinder de Fiestas
 * @notice Este contrato permite a usuarios registrar su asistencia a eventos de forma verificable
 * 
 * Versión: 1.0.0
 * Fecha: Noviembre 2025
 */
contract ProofOfPresence {
    
    // ============================================
    // STATE VARIABLES
    // ============================================
    
    /// @notice Estructura que representa un check-in
    struct CheckIn {
        address user;           // Usuario que hizo check-in
        string location;        // Ubicación del evento
        uint256 timestamp;      // Momento del check-in
        uint256 eventId;        // ID del evento
    }

    /// @notice Estadísticas de un evento
    struct EventStats {
        uint256 totalCheckIns;  // Total de check-ins
        uint256 uniqueUsers;    // Usuarios únicos
        bool exists;            // Si el evento tiene check-ins
    }
    
    /// @notice Mapping de check-ins por usuario
    mapping(address => CheckIn[]) public userCheckIns;
    
    /// @notice Mapping para prevenir duplicados: user => eventId => hasCheckedIn
    mapping(address => mapping(uint256 => bool)) public hasCheckedIn;
    
    /// @notice Estadísticas por evento
    mapping(uint256 => EventStats) private eventStats;
    
    /// @notice Lista de asistentes por evento
    mapping(uint256 => address[]) private eventAttendees;
    
    /// @notice Owner del contrato
    address public owner;
    
    // ============================================
    // EVENTS
    // ============================================
    
    /// @notice Emitido cuando un usuario hace check-in a un evento
    event EventCheckedIn(
        address indexed user,
        uint256 indexed eventId,
        string location,
        uint256 timestamp
    );
    
    /// @notice Emitido cuando se crea un nuevo evento (primer check-in)
    event EventCreated(
        uint256 indexed eventId,
        uint256 timestamp
    );
    
    /// @notice Emitido cuando se transfiere el ownership
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );
    
    // ============================================
    // MODIFIERS
    // ============================================
    
    /// @notice Solo permite que el owner ejecute la función
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    /// @notice Valida que el event ID sea válido (mayor a 0)
    modifier validEventId(uint256 _eventId) {
        require(_eventId > 0, "Invalid event ID");
        _;
    }
    
    // ============================================
    // CONSTRUCTOR
    // ============================================
    
    /// @notice Constructor que establece el owner inicial
    constructor() {
        owner = msg.sender;
    }
    
    // ============================================
    // MAIN FUNCTIONS
    // ============================================
    
    /**
     * @notice Registra asistencia a un evento
     * @dev Valida duplicados y actualiza estadísticas
     * @param _eventId ID del evento (debe ser > 0)
     * @param _location Ubicación del evento (no puede estar vacía)
     */
    function checkInEvent(uint256 _eventId, string memory _location) 
        public 
        validEventId(_eventId)
    {
        // Validar que no esté vacía la ubicación
        require(bytes(_location).length > 0, "Location cannot be empty");
        
        // Prevenir duplicados
        require(
            !hasCheckedIn[msg.sender][_eventId], 
            "Already checked in to this event"
        );
        
        // Crear el check-in
        CheckIn memory newCheckIn = CheckIn({
            user: msg.sender,
            location: _location,
            timestamp: block.timestamp,
            eventId: _eventId
        });
        
        // Guardar en storage
        userCheckIns[msg.sender].push(newCheckIn);
        hasCheckedIn[msg.sender][_eventId] = true;
        
        // Actualizar estadísticas del evento
        if (!eventStats[_eventId].exists) {
            eventStats[_eventId].exists = true;
            emit EventCreated(_eventId, block.timestamp);
        }
        
        eventStats[_eventId].totalCheckIns++;
        eventAttendees[_eventId].push(msg.sender);
        eventStats[_eventId].uniqueUsers = eventAttendees[_eventId].length;
        
        // Emitir evento
        emit EventCheckedIn(
            msg.sender, 
            _eventId, 
            _location, 
            block.timestamp
        );
    }
    
    // ============================================
    // VIEW FUNCTIONS - USER QUERIES
    // ============================================
    
    /**
     * @notice Obtiene todos los check-ins de un usuario
     * @param _user Dirección del usuario
     * @return Array de check-ins del usuario
     */
    function getUserCheckIns(address _user) 
        public 
        view 
        returns (CheckIn[] memory) 
    {
        return userCheckIns[_user];
    }
    
    /**
     * @notice Obtiene el número total de check-ins de un usuario
     * @param _user Dirección del usuario
     * @return Número de check-ins
     */
    function getUserCheckInCount(address _user) 
        public 
        view 
        returns (uint256) 
    {
        return userCheckIns[_user].length;
    }
    
    /**
     * @notice Verifica si un usuario hizo check-in a un evento
     * @param _user Dirección del usuario
     * @param _eventId ID del evento
     * @return true si el usuario hizo check-in, false en caso contrario
     */
    function hasUserCheckedIn(address _user, uint256 _eventId) 
        public 
        view 
        returns (bool) 
    {
        return hasCheckedIn[_user][_eventId];
    }
    
    /**
     * @notice Obtiene el último check-in de un usuario
     * @dev Revierte si el usuario no tiene check-ins
     * @param _user Dirección del usuario
     * @return El último check-in del usuario
     */
    function getLastCheckIn(address _user) 
        public 
        view 
        returns (CheckIn memory) 
    {
        require(userCheckIns[_user].length > 0, "No check-ins found");
        return userCheckIns[_user][userCheckIns[_user].length - 1];
    }
    
    // ============================================
    // VIEW FUNCTIONS - EVENT QUERIES
    // ============================================
    
    /**
     * @notice Obtiene estadísticas de un evento
     * @param _eventId ID del evento
     * @return totalCheckIns Total de check-ins
     * @return uniqueUsers Usuarios únicos
     * @return exists Si el evento tiene check-ins
     */
    function getEventStats(uint256 _eventId) 
        public 
        view 
        returns (uint256 totalCheckIns, uint256 uniqueUsers, bool exists) 
    {
        EventStats memory stats = eventStats[_eventId];
        return (stats.totalCheckIns, stats.uniqueUsers, stats.exists);
    }
    
    /**
     * @notice Obtiene la lista de asistentes a un evento
     * @param _eventId ID del evento
     * @return Array de direcciones de los asistentes
     */
    function getEventAttendees(uint256 _eventId) 
        public 
        view 
        returns (address[] memory) 
    {
        return eventAttendees[_eventId];
    }
    
    // ============================================
    // OWNER FUNCTIONS
    // ============================================
    
    /**
     * @notice Transfiere el ownership del contrato
     * @dev Solo puede ser llamado por el owner actual
     * @param newOwner Nueva dirección del owner
     */
    function transferOwnership(address newOwner) 
        public 
        onlyOwner 
    {
        require(newOwner != address(0), "Invalid address");
        
        address previousOwner = owner;
        owner = newOwner;
        
        emit OwnershipTransferred(previousOwner, newOwner);
    }
}