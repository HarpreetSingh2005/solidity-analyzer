// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe vesting wallet that correctly calculates the released amount based on elapsed time.
contract SafeVesting {
    address public beneficiary;
    uint256 public start;
    uint256 public duration;
    uint256 public released;

    event Released(uint256 amount);

    constructor(address _beneficiary, uint256 _duration) {
        require(_beneficiary != address(0), "Invalid beneficiary");
        beneficiary = _beneficiary;
        start = block.timestamp;
        duration = _duration;
    }

    function release() public {
        require(msg.sender == beneficiary, "Only beneficiary can release");
        
        uint256 unreleased = releasableAmount();
        require(unreleased > 0, "No tokens to release");

        released += unreleased;

        (bool success, ) = beneficiary.call{value: unreleased}("");
        require(success, "Transfer failed");

        emit Released(unreleased);
    }

    function releasableAmount() public view returns (uint256) {
        return vestedAmount() - released;
    }

    function vestedAmount() public view returns (uint256) {
        uint256 totalBalance = address(this).balance + released;

        if (block.timestamp >= start + duration) {
            return totalBalance;
        } else {
            return (totalBalance * (block.timestamp - start)) / duration;
        }
    }

    receive() external payable {}
}