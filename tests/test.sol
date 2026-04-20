// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ClassicReentrancy {
    mapping(address => uint) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint amount = balances[msg.sender]; // READS state var: balances

        (bool success, ) = msg.sender.call{value: amount}(""); // EXTERNAL CALL
        require(success);

        balances[msg.sender] = 0; // WRITES state var: balances (VIOLATION!)
    }
}

contract DecoyReentrancy {
    mapping(address => uint) public balances;
    mapping(address => uint) public lastWithdrawTime;

    function withdraw() external {
        uint amount = balances[msg.sender]; // READS: balances

        (bool success, ) = msg.sender.call{value: amount}(""); // EXTERNAL CALL
        require(success);

        // DECOY: Updated after call, but NEVER read before call. Tool should ignore this.
        lastWithdrawTime[msg.sender] = block.timestamp;

        // TRUE THREAT: Read before, written after. Tool should flag ONLY this.
        balances[msg.sender] = 0;
    }
}

contract BadAccessControl {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // VULNERABILITY: Anyone can call this and become the owner!
    function claimOwnership(address newOwner) public {
        owner = newOwner;
    }
}

contract SafeBank {
    mapping(address => uint) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint amount = balances[msg.sender]; // 1. CHECKS (Read state)

        balances[msg.sender] = 0; // 2. EFFECTS (Write state BEFORE call)

        (bool success, ) = msg.sender.call{value: amount}(""); // 3. INTERACTIONS
        require(success);
    }
}

// --- SHADOWING TESTS ---
contract Parent {
    address public owner;
}

contract Child is Parent {
    // VULNERABILITY: Shadows Parent's 'owner'
    address public owner;

    constructor() {
        owner = msg.sender; // This updates Child.owner, NOT Parent.owner!
    }
}

contract SafeChild is Parent {
    // SAFE: Uses a different name
    address public admin;
}

// --- TX.ORIGIN TESTS ---
contract PhishingWallet {
    address public owner;
    constructor() {
        owner = msg.sender;
    }

    // VULNERABILITY: Uses tx.origin
    function transferAll(address _to) public {
        if (tx.origin == owner) {
            payable(_to).transfer(address(this).balance);
        }
    }
}

contract SafeWallet {
    address public owner;
    constructor() {
        owner = msg.sender;
    }

    // SAFE: Uses msg.sender
    function transferAll(address _to) public {
        require(msg.sender == owner, "Not owner");
        payable(_to).transfer(address(this).balance);
    }
}

// --- SELFDESTRUCT TESTS ---
contract KillSwitch {
    // VULNERABILITY: No access control
    function destroy() public {
        selfdestruct(payable(msg.sender));
    }
}

contract SafeKillSwitch {
    address public owner;
    constructor() {
        owner = msg.sender;
    }

    // SAFE: Has modifier
    function destroy() public onlyOwner {
        selfdestruct(payable(owner));
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
}
