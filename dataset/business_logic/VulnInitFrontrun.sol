// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnInitFrontrun {
    address public owner;
    bool public initialized;

    // Vulnerability: Unprotected initialize function can be front-run
    function initialize() external {
        require(!initialized, "Already initialized");
        owner = msg.sender;
        initialized = true;
    }

    function withdrawAll() external {
        require(msg.sender == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }
}