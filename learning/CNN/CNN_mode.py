{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "class CNN(nn.Module):\n",
    "    def __init__(self):\n",
    "        super(CNN,self).__init__()\n",
    "        self.conv1 = nn.Conv2d(1,16,5,stride = 1,padding = 2)\n",
    "        self.pool = nn.Maxpool2d(kernel_size = 2)\n",
    "        self.conv2 = nn.Conv2d(16,32,5,1,2)\n",
    "        self.out = nn.Linear(32 * 7*7, 10)\n",
    "        \n",
    "    def forward(self, x):\n",
    "        x = self.pool(nn.ReLu(self.conv1(x)))\n",
    "        x = self.pool(nn.ReLu(self.conv2(x)))\n",
    "        x = x.view(x.size(0), -1)\n",
    "        output = self.out(x)\n",
    "        \n",
    "        return output\n",
    "        \n",
    "        \n",
    "            "
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
