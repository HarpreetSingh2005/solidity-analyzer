// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Assuming private variables are secret.
contract VulnNewHiddenState {
    uint256 private secretPassword = 12345;
    function guess(uint256 _password) external {
        require(_password == secretPassword, "Wrong");
        // Attacker can read 'secretPassword' from the blockchain storage directly
    }
}