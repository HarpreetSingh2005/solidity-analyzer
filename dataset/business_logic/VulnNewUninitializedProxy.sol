// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Uninitialized proxy allows anyone to initialize and take ownership.
contract VulnNewUninitializedProxy {
    bool public initialized;
    address public admin;
    function init() external {
        require(!initialized, "Initialized");
        initialized = true;
        admin = msg.sender; // Frontrunnable
    }
}