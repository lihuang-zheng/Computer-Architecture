"""CPU functionality."""
import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.running = True
        self.sp = 7
        self.reg[self.sp] = 0xf4
        self.flag = 0
        self.branch_table = {
            0b10000010: self.handle_ldi,
            0b00000001: self.handle_hlt,
            0b01000111: self.handle_prn,
            0b10100010: self.handle_mul,
            0b10100000: self.handle_add,
            0b10100001: self.handle_sub,
            0b01000110: self.handle_pop,
            0b01000101: self.handle_push,
            0b01010000: self.handle_call,
            0b00010001: self.handle_ret,
            0b10100111: self.handle_cmp,
            0b01010100: self.handle_jmp,
            0b01010110: self.handle_jne,
            0b01010101: self.handle_jeq
        }

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_hlt(self, operand_a, operand_b):
        self.running = False
        self.pc += 1

    def handle_prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def handle_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def handle_add(self, operand_a, operand_b):
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def handle_sub(self, operand_a, operand_b):
        self.alu('SUB', operand_a, operand_b)
        self.pc += 3

    def handle_pop(self, operand_a, operand_b):
        value = self.ram[self.reg[self.sp]]
        self.reg[self.ram[self.pc + 1]] = value
        self.reg[self.sp] += 1
        self.pc += 2

    def handle_push(self, operand_a, operand_b):
        self.reg[self.sp] -= 1
        value = self.reg[self.ram[self.pc + 1]]
        self.ram[self.reg[self.sp]] = value
        self.pc += 2

    def handle_call(self, operand_a, operand_b):
        # Get address of next opcode
        ret_address = self.pc + 2
        # Push onto stack
        self.reg[self.sp] -= 1
        push_address = self.reg[self.sp]
        self.ram[push_address] = ret_address
        # Set pc to subroutine address
        reg_num = self.ram[self.pc + 1]
        subr_address = self.reg[reg_num]
        self.pc = subr_address

    def handle_ret(self, operand_a, operand_b):
        # Get return address from top of stack
        pop_address = self.reg[self.sp]
        ret_address = self.ram[pop_address]
        self.reg[self.sp] += 1
        # Set pc to return address
        self.pc = ret_address

    def handle_cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def handle_jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def handle_jeq(self, operand_a, operand_b):
        if self.flag & 0b1 == 1:
            self.handle_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def handle_jne(self, operand_a, operand_b):
        if self.flag & 0b1 == 0:
            self.handle_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def load(self):
        """Load a program into memory."""
        address = 0
        # file = sys.argv[1]
        try:
            with open("examples/sctest.ls8") as f:
                for line in f:
                    try:
                        line = line.split('#', 1)[0].strip()
                        self.ram[address] = int(line, 2)
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Error, can't find file {sys.argv[1]}")
            sys.exit(1)

    def alu(self, op, operand_a, operand_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[operand_a] += self.reg[operand_b]
        elif op == "MUL":
            self.reg[operand_a] *= self.reg[operand_b]
        elif op == "SUB":
            self.reg[operand_a] -= self.reg[operand_b]
        elif op == "CMP":
            if self.reg[operand_a] == self.reg[operand_b]:
                self.flag = 0b00000001
            elif self.reg[operand_a] < self.reg[operand_b]:
                self.flag = 0b00000100
            elif self.reg[operand_a] < self.reg[operand_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            opcode = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            try:
                self.branch_table[opcode](operand_a, operand_b)
            except:
                print(f'Unknown command: {opcode}')
